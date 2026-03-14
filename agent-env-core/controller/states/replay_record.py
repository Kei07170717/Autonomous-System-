from __future__ import annotations
from ..base_state import State
from . import reset
import dm_env
from agent import RotatingAgent
from core.interfaces import Agent
from environment import Environment

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..controller import ANCController

class ReplayRecordingState(State):
    """
    This state is meant for running the replay of KinestheticAgent recorded
    actions. It should have the actual Body without dummy components. The Observer
    is assumed to be composed of camera(s) and the JointAngles sensor. This state 
    should have a ReplayAgent which sends the actions from a file to the RecordedEnvironment.
    """
  
    def __init__(self, context: ANCController, verbose_mode: bool = True):
        super().__init__(context, state_name="ReplayRecording")
        assert self.context.live_body is not None
        
        self.environment: dm_env.Environment = Environment(self.context.observer, self.context.live_body)
        self.agent: Agent = RotatingAgent()
        self.verbose_mode = verbose_mode

    def on_state_enter(self):
        self.timestep = self.environment.reset()

    def on_state_exit(self):
        pass

    def execute(self):
        assert self.timestep is not None

        action = self.agent.get_action(self.timestep.observation)
        if self.verbose_mode: print("Action: ", action.arm)
        self.observation = self.environment.step(action)
        if self.verbose_mode: print("Obs: ", self.observation.observation)

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
