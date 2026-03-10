from .types import Action
from abc import ABC, abstractmethod

"""Contains the core interfaces that the application depends on."""


class ISensor(ABC):
    """Interface for all sensors"""
    @abstractmethod
    def get_data(self) -> any:
        pass


class IBody(ABC):
    """Capable of affecting the world."""
    @abstractmethod
    def affect_world(self, action: Action) -> None:
        # Apply action to the world
        pass


class IArmActuator(ABC):
    @abstractmethod
    def set_joint_angles(self, arm_pos: list[float]):
        pass


class IArmSensor(ISensor):
    @abstractmethod
    def get_joint_angles(self) -> list[float]:
        pass


class IGripperActuator(ABC):
    @abstractmethod
    def set_gripper_closed(self) -> None:
        pass

    @abstractmethod
    def set_gripper_open(self) -> None:
        pass

    @abstractmethod
    def set_gripper_value(self, value) -> None:
        pass


class IResettable(ABC):
    """
    Interface used for objects that reset (such as cobot)
    """
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def is_reset(self):
        pass

# TODO: should it be an interface or an abstract class?
class Agent(ABC):
    @abstractmethod
    def get_action(self, obs: dict) -> Action:
        pass


class IObserver(ABC):
    """
    Responsible for managing sensors and returning a 'formal' observation.
    """
    @abstractmethod
    def get_observation(self) -> dict:
        pass
