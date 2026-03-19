import numpy as np
from numpy._typing import NDArray
from core.interfaces import IArmActuator, IGripperActuator, IJointAnglesSensor, IResettable, IGripperSensor
import time

class DummyComponent(IArmActuator, IGripperActuator, IJointAnglesSensor, IResettable, IGripperSensor):

    def __init__(self, time_to_reset: int=1) -> None:
        # self.is_resetting: bool = False
        self.time_to_reset = time_to_reset
        self.reset_timestamp = float('inf')
        

    def set_joint_angles(self, arm_pos: list[float]):
        pass

    def set_gripper_closed(self) -> None:
        pass

    def set_gripper_open(self) -> None:
        pass

    def set_gripper_value(self, value) -> None:
        pass

    def get_gripper_value(self):
        return 0 #returns closed gripper

    def get_joint_angles(self) -> NDArray:
        return np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    def reset(self):
        # if self.is_resetting:
        #     return
        self.reset_timestamp = (time.time() * 1000) + self.time_to_reset * 1000
        # self.is_resetting = True

    def is_reset(self) -> bool:
        # if not self.is_resetting:
        #     return False

        reset_done = self.reset_timestamp < (time.time() * 1000)
        return reset_done

    def release_joints(self):
        pass
