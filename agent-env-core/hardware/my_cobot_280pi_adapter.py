import time
import numpy as np
from numpy._typing import NDArray
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
from core.interfaces import IArmActuator, IJointAnglesSensor, IGripperActuator, IJointAnglesSensor, IResettable, IGripperSensor, IColorChanger
from core.types import Action
import math
import random
from util.utils import time_it

_MC_ERROR = -1 # Returned on serial timeouts

_GRIPPER_CLOSED_VALUE = 0 # Gripper min
_GRIPPER_OPEN_VALUE = 100 # Gripper max

# Values higher than this are considered 'closed' (TODO: justify this number)
_GRIPPER_CLOSED_THRESHOLD = int(0.90 * _GRIPPER_OPEN_VALUE) 
_RESET_ANGLES: NDArray = np.array([0,0,0,-70,0,-45]) # We consider these angles to be the idle pos

class MyCobot280PiAdapter(IArmActuator, IJointAnglesSensor, IGripperActuator, IResettable, IGripperSensor, IColorChanger):
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
        init_gripper_val: int = self.get_gripper_value()
        self.is_last_gripper_state_close: bool = self._gripper_value_to_is_closed_bool(init_gripper_val)
        self.last_angles = np.array([])
        self.last_gripper_val = init_gripper_val
        self.target_reset_angles = _RESET_ANGLES.tolist()

#        original_read = self.mc._read
#
#        # 2. Create a wrapper that forces the timeout parameter into the library's function
#        def fast_read(genre, **kwargs):
#            return original_read(genre, timeout=0.07, **kwargs)
#
#        # 3. Overwrite the library's read function with our fast version
#        self.mc._read = fast_read


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
            self.mc.set_gripper_state(int(is_closing_value), self.speed_gripper)
        #self.mc.set_gripper_value(int(gripper_pos), self.speed_gripper)

    @time_it
    def set_gripper_state(self, close: bool):
        if self.is_last_gripper_state_close != close:
            success = self.mc.set_gripper_state(int(close), self.speed_gripper)
            if success is not _MC_ERROR:
                self.is_last_gripper_state_close = close
        else:
            return

    def set_gripper_closed(self) -> None:
        self.mc.set_gripper_value(_GRIPPER_CLOSED_VALUE, self.speed_gripper)

    def set_gripper_open(self) -> None:
        self.mc.set_gripper_value(_GRIPPER_OPEN_VALUE, self.speed_gripper)

    def get_joint_angles(self) -> NDArray[np.float32]:
        # return self.mc.get_angles()
        angles = self.mc.get_angles()
        if angles is _MC_ERROR:
            print("Warning: failed to read joint angles")
            return self.last_angles
        self.last_angles = np.array(angles, dtype=np.float32)
        return self.last_angles


    # actually this might cause issue, needs to be list[float]
    @time_it
    def set_joint_angles(self, arm_pos: NDArray[np.float32]) -> None:
        self.mc.send_angles(arm_pos.tolist(), self.speed_arm)

    def release_joints(self) -> None:
        self.mc.release_all_servos()

    # Maybe there is a numpy function for this? Surely it's performant enough though..
    def _gripper_value_to_is_closed_bool(self, gripper_val) -> bool:
        return False if gripper_val > _GRIPPER_CLOSED_THRESHOLD  else True
    
    def is_reset(self) -> bool:
        return np.allclose(np.array(self.get_joint_angles()), self.target_reset_angles, atol=2)        
        

    def reset(self, randomize: bool=True):
        # self.mc.focus_all_servos()
        self.set_gripper_open()
        success = self.mc.send_coord(3, 300, 50)
        while success == _MC_ERROR:
            success = self.mc.send_coord(3, 300, 50)
        time.sleep(1)
        
        if randomize: 
            random_coords = generate_random_reset_coords()
            random_joint_angles = self.mc.solve_inv_kinematics(random_coords, self.mc.get_angles())
            self.target_reset_angles = random_joint_angles
        is_resetting = self.mc.send_angles(self.target_reset_angles, 10)
        while is_resetting == _MC_ERROR:
            print("Warning: mc not listening to reset")
            time.sleep(0.005)
            is_resetting = self.mc.send_angles(self.target_reset_angles, 10)
   
    @time_it
    def get_gripper_value(self) -> int:
        """Gets gripper values  between 0-100. For some reason can
        also return negative values (would be nice to add to 280PI documentation)"""
        val = self.mc.get_gripper_value()
        if val > 100:
            print(f"Warning, gripper returned higher value than promised: {val} ~ expected max: {_GRIPPER_OPEN_VALUE}")
            return min(100, val)
        elif val < 0:
            print(f"Warning, gripper returned lower value than promised: {val} ~ expected min: {_GRIPPER_CLOSED_VALUE}, copying last value")
            return self.last_gripper_val
        self.last_gripper_val = val
        return val
    
    def set_color(self, color: tuple[str, int, int, int]):
        return self.mc.set_color(color[1], color[2], color[3])

def normalize_angle(angle):
    return (angle + 180) % 360 - 180

def generate_random_reset_coords():
    # Position logic
    radius = random.uniform(170.0, 240.0)
    angle = random.uniform(-math.pi/2, math.pi/2)
    
    # Clamp to API limits
    x = max(min(radius * math.cos(angle), 281.45), 100.45)
    y = max(min(radius * math.sin(angle), 281.45), -281.45)
    z = random.uniform(140.0, 220.0)

    # Orientation logic
    rx = normalize_angle(random.uniform(150.0, 210.0))
    ry = random.uniform(-40.0, 40.0)
    rz = random.uniform(-90.0, 0)
    
    coords = [x, y, z, rx, ry, rz]
    return [round(val, 2) for val in coords]
