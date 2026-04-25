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
from environment.observer import Observer, OptimizedCobotObserver
from hardware.camera import Camera, FrameNotReadyError, NullFrameReturnedError
from hardware.dummy_components import DummyComponent
from hardware.my_cobot_280pi_adapter import MyCobot280PiAdapter
import time

"""'Quick' and dirty code"""
class SemiDummyObserverBuilder():
    def __init__(self) -> None:
        self.sensor_modules: list[SensorModule] = []
        self.dummy_component: DummyComponent = DummyComponent()

    def build_and_register_camera_module(self, label: str, device_name: str, vla_preprocess: bool = False, rotate_90deg_left: bool = False) -> Camera | None:
        cam: Camera | None = None
        try:
            cam = Camera(
                camera_name=device_name, 
                resize_center_crop=vla_preprocess, 
                rotate_90deg_left=rotate_90deg_left
            )
        except ValueError as e:
            # Catches the specific ValueError raised in Camera.get_camera_path()
            print(f"Path/Name error for {label} ({device_name}): {e}")
            return None
        except Exception as e:
            # Catches everything else and prints the ACTUAL error message
            print(f"Unexpected error initializing {label} ({device_name}): {type(e).__name__} - {e}")
            return None
            

        assert cam is not None
        # time.sleep(1)
        inference_attempt_count: int = 0
        print("Inferring TensorSpec from", label, end="", flush=True)
        # get a sample tensor so we can infer the shape and type
        while True:
            try:
                sample_tensor = cam.get_current_frame()
                shape = sample_tensor.shape
                tensor_dtype = sample_tensor.dtype
                tensor_spec = TensorSpec(shape, cast(DTypeLike, tensor_dtype))
                self.sensor_modules.append(
                    CameraSensorModule(label, tensor_spec, camera_sensor=cam)
                )
                print(f"\nSet up {label} with name: \"{device_name}\" ~ and dimensions: {shape}")
                break

            except NullFrameReturnedError:
                print(f"\nCam: {label} returned an invalid frame, skipping {device_name} setup.")
                return None

            except FrameNotReadyError:
                print(".", end="", flush=True)
                time.sleep(0.1)

        print(f"\nDone initializing {label}")
        print(f"  ↳ Configuration:")
        print(f"      • to_rgb:             {cam.to_rgb}")
        print(f"      • resize_center_crop: {cam.resize_center_crop}")
        print(f"      • rotate_90deg_left:  {cam.rotate_90deg_left}\n", flush=True)
        return cam

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
    
    def get_observer(self) -> IObserver:
        return OptimizedCobotObserver(self.sensor_modules)
