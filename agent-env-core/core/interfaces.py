from .types import Action
from abc import ABC, abstractmethod
import torch

"""Contains the core interfaces that the application depends on."""


# class ISensor(ABC):
#     """Interface for all sensors"""
#     @abstractmethod
#     def get_data(self) -> any:
#         pass

class SensorModule(ABC):
    def __init__(self, id: str) -> None:
        self.id: str = id

    def get_id(self) -> str:
        return self.id

    @abstractmethod
    def get_data(self):
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



class IGripperActuator(ABC):
    @abstractmethod
    def set_gripper_closed(self) -> None:
        pass

    @abstractmethod
    def set_gripper_open(self) -> None:
        pass

    @abstractmethod
    def set_gripper_value(self, value: int) -> None:
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
    Responsible for managing sensor-modules and returning a 'formal' observation.
    """
    @abstractmethod
    def get_observation(self) -> dict:
        pass

# --- sensor modules ---
class IJointAnglesSensor(ABC):
    @abstractmethod
    def get_joint_angles(self) -> list[float]:
        pass

class JointAnglesSensorModule(SensorModule):
    def __init__(self, id: str, joint_angles_sensor: IJointAnglesSensor) -> None:
        super().__init__(id)
        self.joint_angles_sensor = joint_angles_sensor

    def get_data(self) -> any:
        return self.joint_angles_sensor.get_joint_angles()

class ICameraSensor(ABC):
    # TODO: return tensor
    @abstractmethod
    def get_current_frame(self):
        pass

class CameraSensorModule(SensorModule):
    def __init__(self, id: str, camera_sensor: ICameraSensor) -> None:
        super().__init__(id)
        self.camera_sensor = camera_sensor

    def get_data(self):
        return self.camera_sensor.get_current_frame()
