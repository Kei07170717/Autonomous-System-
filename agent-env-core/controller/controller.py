from __future__ import annotations
from abc import ABC, abstractmethod
import threading
import time
import gc


from core.interfaces import BaseWriter, IAnnotator, IObserver, IResettable, IArmActuator, IColorChanger
from controller.ghost_image_service import IGhostImageServer
from core.types import SpecTree
from envio.episode_manager import ActionSequenceManager, IActionSequenceManager
from environment import Body, IBody
from environment.environment import Environment, WrittenEnvironment
from remote.interfaces import IRemoteActionProvider
from .states import ResettingState
from .base_state import State

class IANCController(ABC):

    @abstractmethod
    def set_state(self, state: State):
        pass

    @abstractmethod
    def run_loop(self, terminate_event: threading.Event):
        pass
    
    @abstractmethod
    def set_annotator(self, annotator: IAnnotator):
        pass

    @abstractmethod
    def get_annotator(self) -> IAnnotator | None:
        pass

    @abstractmethod
    def open_gripper(self):
        pass

    @abstractmethod
    def close_gripper(self):
        pass

    @abstractmethod
    def start_replay_record(self):
        pass

    
    # @abstractmethod
    # def stop_replay_record(self):
    #     pass

    @abstractmethod
    def start_drag_record(self):
        pass

    @abstractmethod
    def start_inference(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    # @abstractmethod
    # def stop_drag_record(self):
    #     pass

    # @abstractmethod
    # def start_inference(self):
    #     pass
    #
    # @abstractmethod
    # def stop_inference(self):
    #     pass

    @abstractmethod
    def take_ref_image(self):
        pass

    @abstractmethod
    def set_instruction(self, instruction: str):
        pass
    
    @abstractmethod
    def get_instruction(self) -> str:
        pass

    @abstractmethod
    def reset(self):
        pass



class ANCController(IANCController):
    """
    This class controlls the program using states (state design pattern).
    The ANCController has its own loop and will delegate its corresponding 
    actions to the underlying states. ANCController can serve as a 'backbone'
    for a UI.
    It receives a drag_body and optionally a live_body. The drag_body is a 
    simply dummy body that doesn't do anything, even when sending actions.
    The live_body is composed of the actual actuators, sending an action will
    have impact on the environment and hence should be used for
    ReplayRecordingState or other automated motion states.
    """
    def __init__(self,
                 drag_body: IBody,
                 observer: IObserver,
                 arm_actuator: IArmActuator,
                 obs_spec: SpecTree,
                 action_spec: SpecTree,
                 live_body: IBody | None = None,
                 resettable: IResettable | None = None,
                 color_changer: IColorChanger | None = None,
                 hz: float = 20.0,
                 writer: BaseWriter | None = None,
                 annotator: IAnnotator | None = None,
                 ghost_image_server: IGhostImageServer | None = None,
                 remote_action_provider: IRemoteActionProvider | None = None
                 ):
        
        self.observer: IObserver = observer
        self.obs_spec: SpecTree = obs_spec
        self.action_spec: SpecTree = action_spec
        self.drag_body: IBody | None = drag_body
        self.live_body: IBody | None = live_body
        self.resettable: IResettable | None = resettable
        self.arm_actuator: IArmActuator = arm_actuator
        self._state_lock = threading.RLock()
        self.color_changer: IColorChanger | None = color_changer
        self.loop_period = 1.0 / hz
        self.terminate_event: bool = False # Terminates loop (but doesn't get set anywhere..)
        self.action_sequence_manager: IActionSequenceManager = ActionSequenceManager() # TODO: Offload to composition root'
        self.writer: BaseWriter | None = writer
        self.annotator = annotator
        self.ghost_image_server = ghost_image_server
        self.remote_action_provider = remote_action_provider
        
        print("Entering Resetting state")
        self.state: State = ResettingState(self)
        self.state.on_state_enter()

        # print("Max steps")


    
    
    def set_state(self, state: State) -> None:

        with self._state_lock:
            if self.state:
                self.state.on_state_exit()
        
            print("Entering {} state".format(state.get_state_name()))
            self.state = state
            
            self.state.on_state_enter()

            

    def run_loop(self, terminate_event: threading.Event):
        # 1. Disable automatic garbage collection to prevent unpredictable jitter
        gc.disable()
        
        try:
            # Set the first deadline
            next_wake_time = time.perf_counter() + self.loop_period

            while not terminate_event.is_set():
                exec_start = time.perf_counter()

                # Safely execute the current state
                with self._state_lock:
                    self.state.execute()

                now = time.perf_counter()
                exec_duration = now - exec_start
                sleep_duration = next_wake_time - now

                if sleep_duration > 0:
                    # --- GC Optimization ---
                    # If we have a safe margin of idle time, run a Generation 0 collection.
                    # Gen 0 targets the youngest objects and is extremely fast. 
                    # Adjust this threshold (e.g., 0.002s) based on your specific loop period.
                    if sleep_duration > 0.002: 
                        gc.collect(0) 
                        
                        # GC takes time, so we MUST recalculate the remaining sleep duration
                        now = time.perf_counter()
                        sleep_duration = next_wake_time - now
                    
                    # Sleep only if we still have time left after the potential GC run
                    if sleep_duration > 0:
                        time.sleep(sleep_duration)
                        
                    # Step the deadline forward cleanly
                    next_wake_time += self.loop_period 
                else:
                    # OVERRUN handling
                    delay = -sleep_duration
                    print(f"OVERRUN: Delayed by {delay:.4f}s. "
                          f"Execution took {exec_duration:.4f}s (Budget: {self.loop_period:.4f}s)")
                    
                    # Reset the deadline to be exactly one period from right NOW, 
                    # dropping the missed frames.
                    next_wake_time = time.perf_counter() + self.loop_period

            # Gracefully exit the current state
            self.state.on_state_exit()
            
        finally:
            # 2. Re-enable GC when the loop exits so the rest of your app doesn't leak memory
            gc.enable()
    def set_annotator(self, annotator: IAnnotator):
        self.annotator = annotator
        if self.writer and self.annotator:
            self.writer.set_episode_end_annotation_callback(self.annotator.get_annotation)

    def get_annotator(self) -> IAnnotator | None:
        return self.annotator

    def open_gripper(self):
        self.state.open_gripper()

    def close_gripper(self):
        self.state.close_gripper()

    def start_replay_record(self):
        self.state.start_replay_record()

    # def stop_replay_record(self):
    #     pass

    def start_drag_record(self):
        self.state.start_drag_record()
    
    def start_inference(self):
        self.state.start_inference()

    def stop(self):
        self.state.stop()

    def take_ref_image(self):
        self.state.take_ref_image()

    # def stop_drag_record(self):
    #     pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    def set_instruction(self, instruction: str):
        self.observer.set_instruction(instruction)

    def get_instruction(self) -> str:
        return self.observer.get_instruction()

    def reset(self):
        self.state.reset()

    


class ICommand(ABC):

    @abstractmethod
    def execute(self) -> None:
        pass
