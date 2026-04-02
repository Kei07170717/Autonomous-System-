from abc import ABC, abstractmethod
from typing import cast
import numpy as np
from numpy._typing import DTypeLike
from core.interfaces import (
    CameraSensorModule,
    GripperSensorModule,
    IJointAnglesSensor,
    IObserver,
    JointAnglesSensorModule,
    SensorModule,
)
from core.types import SpecTree, TensorSpec
from environment.observer import Observer
from hardware.camera import Camera
from hardware.dummy_components import DummyComponent
from hardware.my_cobot_280pi_adapter import MyCobot280PiAdapter

"""'Quick' and dirty code"""
class SemiDummyObserverBuilder():
    def __init__(self) -> None:
        self.sensor_modules: list[SensorModule] = []
        self.dummy_component: DummyComponent = DummyComponent()

    def build_and_register_camera_module(self, label: str, device_name: str) -> bool:
        try:
            cam = Camera(camera_name=device_name)
            # get a sample tensor so we can infer the shape and type
            sample_tensor = cam.get_current_frame_as_tensor()
            shape = sample_tensor.shape
            tensor_dtype = sample_tensor.dtype
            tensor_spec = TensorSpec(shape, cast(DTypeLike, tensor_dtype))
            self.sensor_modules.append(
                CameraSensorModule(label, tensor_spec, camera_sensor=cam)
            )
            return True
        except Exception as e:
            print("Couldn't init camera, most likely wrong path: ", device_name)
            return False

    def register_gripper_sensor_module(self):
        self.sensor_modules.append(GripperSensorModule(
            "gripper",
            TensorSpec((), np.uint8),
            self.dummy_component
            ))

    
    def register_joint_angles_sensor(self):
        self.sensor_modules.append(JointAnglesSensorModule(
            "arm_angles",
            TensorSpec(shape=(6,), dtype=np.float32),
            self.dummy_component
            ))

    def get_observation_spec(self) -> SpecTree:
        if len(self.sensor_modules) == 0:
            return {}

        return {
            sensor.get_id(): sensor.get_return_spec() for sensor in self.sensor_modules
        }

    def get_observer(self) -> IObserver:
        return Observer(self.sensor_modules)


class MyCobot280PIObserverBuilder(SemiDummyObserverBuilder):
    def __init__(self, cobot: MyCobot280PiAdapter):
        super().__init__()
        self.cobot = cobot

    def register_gripper_sensor_module(self, label: str = "gripper"):
        self.sensor_modules.append(
            GripperSensorModule(
                label, TensorSpec((), np.uint8), gripper_sensor=self.cobot
            )
        )

    def register_joint_angles_sensor(self, label: str = "arm_angles"):
        self.sensor_modules.append(
            JointAnglesSensorModule(
                label, TensorSpec(shape=(6,), dtype=np.float32), self.cobot
            )
        )
