from abc import ABC, abstractmethod

import dm_env
import numpy as np
from dm_env import TimeStep, specs

from core.interfaces import BaseWriter, IBody, IObserver
from core.types import Action
from envio.dataset_storage_manager import IDatasetStorageManager
from envio.episode_manager import IActionSequenceManager
from envio.writing import IActionSequenceWriter


class Environment(dm_env.Environment):
    def __init__(self, observer: IObserver, body: IBody, obs_spec, action_spec, max_steps: int =-1):
        self.observer: IObserver = observer
        self.body: IBody = body
        self.obs_spec = obs_spec
        self.action_spec = action_spec
        self.max_steps = max_steps # 'None' on default
        self.current_step_count: int = 0

    # def set_max_steps(self, max_steps: int):
    #     self.max_steps = max_steps
    #
    # def clear_max_steps(self):
    #     self.max_steps = -1

    def reset(self) -> TimeStep:
        self.current_step_count = 0
        observation = self.observer.get_observation()
        return dm_env.restart(
            observation=observation,
        )

    def observation_spec(self):
        # return {
        #     "arm_angles": specs.BoundedArray(
        #         shape=(6,), dtype=np.float32, name="arm_angles", minimum=0, maximum=360 # TODO: Should not be 360!!
        #         ),
        #     "gripper": specs.BoundedArray(
        #         shape=(), dtype=np.uint8, name="gripper", minimum=0, maximum=100 
        #     )
        # }
        return self.obs_spec

    def action_spec(self):
        # return {
        #     "arm_angles": specs.BoundedArray(
        #         shape=(6,), dtype=np.float32, name="arm_angles", minimum=0, maximum=360
        #     ),
        #     "gripper": specs.BoundedArray(
        #         shape=(), dtype=np.uint8, name="gripper", minimum=0, maximum=100 
        #     )
        # }
        return self.action_spec

    def step(self, action: dict) -> TimeStep:
        observation = self.observer.get_observation()
        
        print("ENV STEP: ", self.current_step_count)
        if self.max_steps and self.current_step_count == (self.max_steps - 1):
            return dm_env.termination(observation=observation, reward=np.float32(0.0))

        self.current_step_count += 1

        self.body.affect_world(
            action
        )  # SETTING after GETTING improves performance by a lot for the 280PI for some reason
        return dm_env.transition(observation=observation, reward=np.float32(0.0))


class EnvironmentWrapper(dm_env.Environment):
    def __init__(self, env: dm_env.Environment):
        self.env: dm_env.Environment = env

    # @abstractmethod
    def reset(self) -> TimeStep:
        time_step = self.env.reset()
        # self.steps.append(())
        # self.ep_writer.write_episode(self.steps)
        return time_step

    # @abstractmethod
    def step(self, action) -> TimeStep:
        time_step = self.env.step(action)
        return time_step

    # def reward_spec(self):
    #     pass
    #
    # def discount_spec(self):
    #     pass

    # @abstractmethod
    def observation_spec(self):
        pass

    # @abstractmethod
    def action_spec(self):
        pass

    def close(self):
        pass

    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, exc_type, exc_value, traceback):
    #     pass

class ActionRecordedEnvironment(EnvironmentWrapper):
    def __init__(self, env: dm_env.Environment, action_writer: IActionSequenceWriter, action_sequence_manager: IActionSequenceManager):
       super().__init__(env)
       self.actions: list[Action] = []
       self.action_writer: IActionSequenceWriter = action_writer
       self.action_sequence_manager = action_sequence_manager

    def step(self, action) -> TimeStep:
        self.actions.append(action)
        return super().step(action)

    def __del__(self): # Maybe a bit unsafe?
        self.action_sequence_manager.set_actions(self.actions)
        self.action_writer.write_episode(self.actions)


class WrittenEnvironment(EnvironmentWrapper):
    # def __init__(self, env: dm_env.Environment, writer: BaseWriter, dataset_storage_manager: IDatasetStorageManager):
    def __init__(self, env: dm_env.Environment, writer: BaseWriter):
        self._env = env
        self.writer = writer

    def step(self, action) -> TimeStep:
        timestep = self._env.step(action)
        self.writer.write_step(action, timestep)
        return timestep

    def reset(self) -> TimeStep:
        timestep = self._env.reset()
        self.writer.prepare_new_episode(timestep)
        return timestep
        
