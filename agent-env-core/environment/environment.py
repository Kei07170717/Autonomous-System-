from abc import ABC, abstractmethod

import dm_env
import numpy as np
from dm_env import TimeStep, specs

from core.interfaces import IBody, IObserver
from core.types import Action
from envio.episode_manager import IActionSequenceManager
from envio.writing import IActionSequenceWriter


class Environment(dm_env.Environment):
    def __init__(self, observer: IObserver, body: IBody):

        self.observer: IObserver = observer
        self.body: IBody = body

    def reset(self) -> TimeStep:
        observation = self.observer.get_observation()
        return dm_env.restart(
            observation=observation,
        )

    def observation_spec(self):
        pass

    def action_spec(self):
        pass

    def step(self, action: Action) -> TimeStep:
        observation = self.observer.get_observation()
        self.body.affect_world(
            action
        )  # SETTING after GETTING improves performance by a lot for the 280PI for some reason
        return dm_env.transition(observation=observation, reward=None)


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

    def __del__(self):
        self.action_sequence_manager.set_actions(self.actions)
        self.action_writer.write_episode(self.actions)
