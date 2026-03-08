from .types import Action
from abc import ABC, abstractmethod


class IBody(ABC):
    @abstractmethod
    def affect_world(self, action: Action) -> None:
        # Apply action to the world
        pass


class ISensor(ABC):
    '''Interface for all sensors'''
    @abstractmethod
    def get_data(self) -> any:
        pass


class Agent(ABC):
    @abstractmethod
    def get_action(obs: dict) -> Action:
        pass
