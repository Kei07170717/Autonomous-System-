import dm_env 
from dm_env import specs, _environment, TimeStep
import numpy as np
from abc import ABC, abstractmethod
from core.interfaces import IBody, IObserver



class Environment(dm_env.Environment):
    def __init__(
            self, 
            observer: IObserver):
        
        self.observer: IObserver = observer


    def reset(self) -> TimeStep:
        pass

    def observation_spec(self):
        pass

    def action_spec(self):
        pass

    def step(self):
        pass


class RecordedEnvironment(dm_env.Environment, ABC):
    def __init__(self, env: dm_env.Environment):
        self.env: dm_env.Environment = env

    @abstractmethod
    def reset(self) -> TimeStep:
        pass

    @abstractmethod
    def step(self, action) -> TimeStep:
        pass
    
    def reward_spec(self):
        pass

    def discount_spec(self):
        pass

    @abstractmethod
    def observation_spec(self):
        pass

    @abstractmethod
    def action_spec(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass


class RLDSRecordedEnvironment(RecordedEnvironment):
    def __init__(self):
        super().__init__()
        


