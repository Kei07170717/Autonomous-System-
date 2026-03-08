import time
import numpy as np
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
from core.interfaces import IArmActuator, IArmSensor, IGripperActuator
from core.types import Action

_GRIPPER_OPEN_VALUE = 0
_GRIPPER_CLOSED_VALUE = 100


class MyCobot280PiAdapter(IArmActuator, IArmSensor, IGripperActuator):
    def __init__(
            self,
            PI_PORT,
            PI_BAUD,
            speed_arm=100,  # speed of the robot arm
            speed_gripper=100,  # speed of the gripper
    ):

        self.mc = MyCobot280(PI_PORT, PI_BAUD)
        self.speed_arm = speed_arm
        self.speed_gripper = speed_gripper

    def set_gripper(self, gripper_pos: int) -> None:
        self.mc.set_gripper_value(int(gripper_pos), self.speed_gripper)

    def set_gripper_closed(self) -> None:
        self.mc.set_gripper_value(_GRIPPER_CLOSED_VALUE, self.speed_gripper)

    def set_gripper_open(self) -> None:
        self.mc.set_gripper_value(_GRIPPER_OPEN_VALUE, self.speed_gripper)

    # actually this might cause issue, needs to be list[float]
    def set_joint_angles(self, arm_pos: list[float]) -> None:
        self.mc.send_angles(arm_pos, self.speed_gripper)

    def affect_world(self, action: Action):
        self.set_arm(action.arm)

        if action.gripper is not None:
            self.set_gripper(action.gripper)
