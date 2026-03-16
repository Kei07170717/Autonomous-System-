from __future__ import annotations
from typing import TYPE_CHECKING

from core.interfaces import Agent
from agent import KinestheticAgent
from envio.episode_manager import ActionSequenceManager
from envio.writing import NumpyActionSequenceWriter, IActionSequenceWriter

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
        super().__init__(context, state_name="DragRecording")
        assert self.context.drag_body is not None

        self.environment: dm_env.Environment = Environment(self.context.observer, self.context.drag_body)

        # Decorate the current environment with a recorder
        writer: IActionSequenceWriter = NumpyActionSequenceWriter(write_path="a.txt", metadata=None)
        self.environment: dm_env.Environment = ActionRecordedEnvironment(self.environment, writer, self.context.action_sequence_manager)
        self.agent: Agent = KinestheticAgent()
        self.verbose_mode = verbose_mode
        
    
    def on_state_enter(self):
        self.timestep = self.environment.reset()
        self.context.arm_actuator.release_joints()

    def on_state_exit(self):
        pass

    def execute(self):
        assert self.timestep is not None

        action = self.agent.get_action(self.timestep.observation)
        if self.verbose_mode: print("Action: ", action.arm)
        self.timestep = self.environment.step(action)
        if self.verbose_mode: print("Obs: ", self.timestep.observation)

    def open_gripper(self):
        pass

    def close_gripper(self):
        pass

    def start_replay_record(self):
        pass

    def start_drag_record(self):
        pass

    def stop(self):
        self.context.set_state(reset.ResettingState(self.context))
