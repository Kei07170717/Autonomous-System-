import time
import numpy as np
from numpy._typing import NDArray
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
from core.interfaces import IArmActuator, IJointAnglesSensor, IGripperActuator, IJointAnglesSensor, IResettable
from core.types import Action
import math


_GRIPPER_OPEN_VALUE = 0 # Gripper min
_GRIPPER_CLOSED_VALUE = 100 # Gripper max

# Values higher than this are considered 'closed' (TODO: justify this number)
_GRIPPER_CLOSED_THRESHOLD = int(0.05 * _GRIPPER_CLOSED_VALUE) 
_RESET_ANGLES: NDArray = np.array([0,0,0,0,0,0]) # We consider these angles to be the idle pos

class MyCobot280PiAdapter(IArmActuator, IJointAnglesSensor, IGripperActuator, IResettable):
    def __init__(
            self,
            pi_port=PI_PORT,
            pi_baud=PI_BAUD,
            speed_arm=100,  # speed of the robot arm
            speed_gripper=100,  # speed of the gripper
    ):

        self.mc = MyCobot280(pi_port, str(pi_baud))
        self.speed_arm = speed_arm
        self.speed_gripper = speed_gripper

        # Questionable, but is to get an 'awareness' of our initial state
        # init_gripper_val: int = self.mc.get_gripper_value()
        init_gripper_val: int = 0 # TODO: Implement
        self.is_last_gripper_state_close: bool = self._gripper_value_to_is_closed_bool(init_gripper_val)

    def set_gripper_value(self, value: int) -> None:
        """
        Could theoretically set the gripper to a range of values, 
        but isn't very practical unless high precision is needed. 
        Therefore, it will simply be converted to 'open' or 'closed' by
        converting it to a bool. Might not be ideal though.
        """
        is_closing_value: bool = self._gripper_value_to_is_closed_bool(value)
        if self.is_last_gripper_state_close == is_closing_value:
            return
        else: 
            self.is_last_gripper_state_close = is_closing_value
            self.mc.set_gripper_state(is_closing_value, self.speed_gripper)
        #self.mc.set_gripper_value(int(gripper_pos), self.speed_gripper)

    def set_gripper_closed(self) -> None:
        self.mc.set_gripper_value(_GRIPPER_CLOSED_VALUE, self.speed_gripper)

    def set_gripper_open(self) -> None:
        self.mc.set_gripper_value(_GRIPPER_OPEN_VALUE, self.speed_gripper)

    # BLOCKING CALL!!! Will take long time, carefull
    def get_joint_angles(self) -> list[float]:
        # return self.mc.get_angles()
        return self.mc.get_angles()

    # actually this might cause issue, needs to be list[float]
    def set_joint_angles(self, arm_pos: list[float]) -> None:
        self.mc.send_angles(arm_pos, self.speed_gripper)

    def release_joints(self) -> None:
        """Releases the joints, allowing for manual manipulation."""
        self.mc.release_all_servos()

    # Maybe there is a numpy function for this? Surely it's performant enough though..
    def _gripper_value_to_is_closed_bool(self, gripper_val) -> bool:
        return False if gripper_val < _GRIPPER_CLOSED_THRESHOLD  else True
    
    def is_reset(self) -> bool:
        return np.allclose(np.array(self.get_joint_angles()), _RESET_ANGLES, atol=0.6)        
        

    def reset(self):
        self.mc.send_angles(_RESET_ANGLES.tolist(), 10)
