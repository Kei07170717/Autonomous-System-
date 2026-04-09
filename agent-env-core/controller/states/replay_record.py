from __future__ import annotations

from controller.utils import print_action, print_observation
from environment.environment import WrittenEnvironment
from ..base_state import State
from . import reset
# import envlogger
# from envlogger.backends import tfds_backend_writer
# import tensorflow_datasets as tfds
# import tensorflow as tf
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
        super().__init__(context, state_name="ReplayRecording", color = ("Purple", 225, 213,231 )) 
        
        # self.context.replay_environment: dm_env.Environment | None = None
        self.agent: Agent = RotatingAgent() # ???
        self.verbose_mode = verbose_mode
        

    def on_state_enter(self):
        super().on_state_enter()

        # We can only replay actions present in memory...
        if not self.context.action_sequence_manager.is_episode_recorded():
            print("Could not find recorded actions in memory, exiting ReplayRecordingState...")
            return self.context.set_state(reset.ResettingState(self.context))
            
        self.agent = self.context.action_sequence_manager.create_replay_agent()

        # Replay is infinite, hence we need to have the environment return terminal on last step
        max_steps = len(self.context.action_sequence_manager.get_actions())

        assert self.context.live_body is not None
        self.replay_environment = Environment(self.context.observer, self.context.live_body, obs_spec=self.context.obs_spec, action_spec=self.context.action_spec, max_steps=max_steps)
        
        # Only record if a writer is provided
        if self.context.writer:
            self.replay_environment = WrittenEnvironment(self.replay_environment, self.context.writer)
        self.timestep = self.replay_environment.reset()
        


    def on_state_exit(self):
        # Clean up...
        if self.replay_environment is not None:
            self.replay_environment.close()

    def execute(self):
        assert self.timestep is not None
        assert self.replay_environment is not None

        action = self.agent.get_action(self.timestep.observation)
        if self.verbose_mode: print_action(action)
        self.timestep = self.replay_environment.step(action)
        if self.verbose_mode: print_observation(self.timestep.observation)

        if self.timestep.last():
            self.context.set_state(reset.ResettingState(self.context))
    #add decorator @disabled
    def open_gripper(self):
        pass
    #add decorator @disabled
    def close_gripper(self):
        pass

    def start_replay_record(self):
        pass

    def start_drag_record(self):
        pass

    def stop(self):
        self.context.set_state(reset.ResettingState(self.context))
