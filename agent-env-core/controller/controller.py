from __future__ import annotations
from abc import ABC, abstractmethod
import time
from core.interfaces import IObserver, IResettable
from environment import Body, IBody
from .states import ResettingState
from .base_state import State

class IANCController(ABC):

    @abstractmethod
    def set_state(self, state: State):
        pass

    @abstractmethod
    def run_loop(self):
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
                 live_body: IBody | None = None,
                 resettable: IResettable | None = None,
                 ):
        self.drag_body: IBody | None = drag_body
        self.live_body: IBody | None = live_body
        self.resettable: IResettable | None = resettable
        print("Entering Resetting state")
        self.state: State = ResettingState(self)
        self.terminating: bool = False

    def set_state(self, state: State) -> None:
        print("Entering {} state".format(state.get_state_name()))
        self.state = state

    def run_loop(self):
        while not self.terminating:
            self.state.execute()
            time.sleep(0.1)  # TODO: Remove

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

    def stop(self):
        self.state.stop()

    # def stop_drag_record(self):
    #     pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass

class ICommand(ABC):

    @abstractmethod
    def execute(self) -> None:
        pass





