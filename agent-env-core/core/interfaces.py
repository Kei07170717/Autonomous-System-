from dm_env import TimeStep
from numpy._typing import NDArray
from .types import Action, TensorSpec
from abc import ABC, abstractmethod
from torch import Tensor
import numpy as np
import torch

"""Contains the core interfaces that the application depends on."""


# class ISensor(ABC):
#     """Interface for all sensors"""
#     @abstractmethod
#     def get_data(self) -> any:
#         pass


class SensorModule(ABC):
    def __init__(self, id: str, return_spec: TensorSpec) -> None:
        self.id: str = id
        self.return_spec: TensorSpec = return_spec

    def get_id(self) -> str:
        return self.id

    def get_return_spec(self) -> TensorSpec:
        return self.return_spec

    @abstractmethod
    def get_data(self) -> NDArray:
        pass


class IBody(ABC):
    """Capable of affecting the world."""

    @abstractmethod
    def affect_world(self, action: dict) -> None:
        # Apply action to the world
        pass


class IArmActuator(ABC):
    @abstractmethod
    def set_joint_angles(self, arm_pos: NDArray[np.float32]):
        pass

    @abstractmethod
    def release_joints(self) -> None:
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
    def is_reset(self) -> bool:
        pass


# TODO: should it be an interface or an abstract class?
class Agent(ABC):
    @abstractmethod
    def get_action(self, obs: dict) -> dict:
        pass


class IObserver(ABC):
    """
    Responsible for managing sensor-modules and returning a 'formal' observation.
    """

    @abstractmethod
    def get_observation(self) -> dict:
        pass

    @abstractmethod
    def attach_sensor_module(self, module: SensorModule):
        pass


# --- sensor modules ---
class IJointAnglesSensor(ABC):
    @abstractmethod
    def get_joint_angles(self) -> NDArray[np.float32]:
        pass


class JointAnglesSensorModule(SensorModule):
    def __init__(
        self, id: str, return_spec: TensorSpec, joint_angles_sensor: IJointAnglesSensor
    ) -> None:
        super().__init__(id, return_spec)
        self.joint_angles_sensor = joint_angles_sensor

    def get_data(self) -> NDArray:
        return self.joint_angles_sensor.get_joint_angles()


class ICameraSensor(ABC):
    # TODO: return tensor
    @abstractmethod
    def get_current_frame(self) -> NDArray:
        pass


class CameraSensorModule(SensorModule):
    def __init__(
        self, id: str, return_spec: TensorSpec, camera_sensor: ICameraSensor
    ) -> None:
        super().__init__(id, return_spec)
        self.camera_sensor = camera_sensor

    def get_data(self) -> NDArray:
        return self.camera_sensor.get_current_frame()


class IGripperSensor(ABC):
    """ """

    @abstractmethod
    def get_gripper_value(self) -> float:
        pass


class GripperSensorModule(SensorModule):
    def __init__(
        self, id: str, return_spec: TensorSpec, gripper_sensor: IGripperSensor
    ):
        """Adapter class
        runs the get_data for the Gripper
        returns the gripper (0-100) as Tensor
        """
        super().__init__(id, return_spec)
        self.gripper_sensor = gripper_sensor

    def get_data(self) -> NDArray:
        return np.asarray(self.gripper_sensor.get_gripper_value(), dtype=np.uint8)


class BaseWriter(ABC):
    def __init__(self, obs_spec, action_spec, metadata=None) -> None:
        self.obs_spec = obs_spec
        self.action_spec = action_spec
        # self.dataset_dir = dataset_dir
        self.metadata = metadata or {}
        self.is_annotation_needed: bool = False
        self.end_of_episode_annotation_callback = None

    @abstractmethod
    def prepare_new_episode(self, initial_timestep: TimeStep):
        pass

    @abstractmethod
    def write_step(self, action, timestep: TimeStep):
        pass
    
    @abstractmethod
    def set_annotation(self, annotation: dict):
        pass

    def set_episode_end_annotation_callback(self, func):
        self.end_of_episode_annotation_callback = func

    # def get_is_annotation_needed(self) -> bool:
    #     return self.is_annotation_needed

    @abstractmethod
    def close(self):
        pass

class IAnnotator(ABC):

    @abstractmethod
    def get_annotation(self) -> dict:
        pass
