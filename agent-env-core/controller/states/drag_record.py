from __future__ import annotations
from typing import TYPE_CHECKING

from controller.utils import disabled_in_this_state, print_action, print_observation
from core.interfaces import Agent
from agent import KinestheticAgent
from envio.episode_manager import ActionSequenceManager
from envio.writing import NumpyActionSequenceWriter, IActionSequenceWriter
import threading
if TYPE_CHECKING:
    from ..controller import ANCController

from ..base_state import State
from . import reset
import dm_env
from environment import Environment, ActionRecordedEnvironment


class DragRecordingState(State):
    """
    In this state, the arm should go limp and interaction between
    KinestheticAgent and a child class of RecordedEnvironment should happen.
    This makes it so that the interactions are recorded automatically. 
    This state is meant to be spawned from the IdlingState and transition to
    the ResettingState when done or terminated.
   
    """
  
    def __init__(self, context: ANCController, verbose_mode=True):
        super().__init__(context, state_name="DragRecording", color = ("red", 255, 0, 0))
        assert self.context.drag_body is not None
        self.manual_gripper_state: int | None = None
        self.lock = threading.Lock()

        self.environment: dm_env.Environment = Environment(self.context.observer, self.context.drag_body, obs_spec=self.context.obs_spec, action_spec=self.context.action_spec)

        # Decorate the current environment with a recorder
        writer: IActionSequenceWriter = NumpyActionSequenceWriter(write_path="a.txt", metadata=None)
        self.environment: dm_env.Environment = ActionRecordedEnvironment(self.environment, writer, self.context.action_sequence_manager)
        self.agent: KinestheticAgent = KinestheticAgent()
        self.verbose_mode = verbose_mode
        
    
    def on_state_enter(self):
        super().on_state_enter()
        self.timestep = self.environment.reset()
        self.context.arm_actuator.release_joints()
        


    def on_state_exit(self):
        pass

    def execute(self):
        assert self.timestep is not None
        
        explicit_gripper_state: int | None = self._get_gripper_state_if_explicitly_set() # Overwrite gripper value by UI thread
        if explicit_gripper_state is not None:
            self.agent.set_griper_manually(explicit_gripper_state)

        action = self.agent.get_action(self.timestep.observation)

        if self.verbose_mode: print_action(action)
        self.timestep = self.environment.step(action)
        if self.verbose_mode: print_observation(self.timestep.observation)

    def open_gripper(self):
        with self.lock:
            self.manual_gripper_state = False
        super().open_gripper()

    def close_gripper(self):
        with self.lock:
            self.manual_gripper_state = True
        super().close_gripper()

    @disabled_in_this_state
    def start_replay_record(self):
        pass

    @disabled_in_this_state
    def start_drag_record(self):
        pass

    def stop(self):
        self.context.set_state(reset.ResettingState(self.context))
    
    @disabled_in_this_state
    def take_ref_image(self):
        pass
    
    @disabled_in_this_state
    def start_inference(self):
        pass

    def _get_gripper_state_if_explicitly_set(self) -> int | None:
        with self.lock:
            return self.manual_gripper_state
