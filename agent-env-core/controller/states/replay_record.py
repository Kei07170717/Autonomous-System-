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
        
        self.environment: dm_env.Environment | None = None
        self.agent: Agent = RotatingAgent() # ???
        self.verbose_mode = verbose_mode

    def on_state_enter(self):

        # We can only replay actions present in memory...
        if not self.context.action_sequence_manager.is_episode_recorded():
            print("Could not find recorded actions in memory, exiting ReplayRecordingState...")
            self.context.set_state(reset.ResettingState(self.context))
        else:
            self.agent = self.context.action_sequence_manager.create_replay_agent()
        
        assert self.context.live_body is not None
        max_steps = len(self.context.action_sequence_manager.get_actions())
        self.environment = Environment(self.context.observer, self.context.live_body, max_steps)

        # TODO: place somewhere where it makes sense
        def get_dataset_config():
            return tfds.rlds.rlds_base.DatasetConfig(
                name="my_imitation_dataset",
                observation_info=tfds.features.FeaturesDict({
                    "arm_angles": tfds.features.Tensor(shape=(6,), dtype=tf.float32)}),
                
                action_info=tfds.features.FeaturesDict({
            "arm_angles": tfds.features.Tensor(shape=(6,), dtype=tf.float32),
            "gripper": tfds.features.Tensor(shape=(), dtype=tf.uint8) 
        }),
                # RLDS strictly expects reward and discount fields, even for imitation learning.
                # Your environment can simply return 0.0 for these.
                reward_info=tf.float32,
                discount_info=tf.float64,
            )

        def get_writer(conf):
            return tfds_backend_writer.TFDSBackendWriter(
                data_directory='/tmp/my_il_dataset',
                split_name='train',
                max_episodes_per_file=20,
                ds_config=conf
            )

        self.environment = envlogger.EnvLogger(self.environment, backend=get_writer(get_dataset_config()))
        self.timestep = self.environment.reset()

    def on_state_exit(self):
        assert self.environment is not None
        self.environment.close()

    def execute(self):
        assert self.timestep is not None
        assert self.environment is not None

        action = self.agent.get_action(self.timestep.observation)
        if self.verbose_mode: print("Action: ", action)
        self.timestep = self.environment.step(action)
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
