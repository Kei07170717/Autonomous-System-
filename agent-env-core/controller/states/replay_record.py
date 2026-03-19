from __future__ import annotations
from ..base_state import State
from . import reset
import dm_env
import envlogger
from envlogger.backends import tfds_backend_writer
import tensorflow_datasets as tfds
import tensorflow as tf
from agent import RotatingAgent
from core.interfaces import Agent
from environment import Environment
import numpy as np

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
        
        # self.context.replay_environment: dm_env.Environment | None = None
        self.agent: Agent = RotatingAgent() # ???
        self.verbose_mode = verbose_mode

    def on_state_enter(self):

        # We can only replay actions present in memory...
        if not self.context.action_sequence_manager.is_episode_recorded():
            print("Could not find recorded actions in memory, exiting ReplayRecordingState...")
            return self.context.set_state(reset.ResettingState(self.context))
            
        self.agent = self.context.action_sequence_manager.create_replay_agent()

        # Replay is infinite, hence we need to have the environment return terminal on last step
        max_steps = len(self.context.action_sequence_manager.get_actions())
        self.context.replay_environment.set_max_steps(max_steps)  
        self.timestep = self.context.replay_environment.reset()
        


    def on_state_exit(self):
        pass

    def execute(self):
        assert self.timestep is not None
        assert self.context.replay_environment is not None

        action = self.agent.get_action(self.timestep.observation)
        if self.verbose_mode: print("Action: ", action)
        self.timestep = self.context.replay_environment.step(action)
        if self.verbose_mode: print("Obs: ", self.timestep.observation)

        if self.timestep.last():
            self.context.set_state(reset.ResettingState(self.context))

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
