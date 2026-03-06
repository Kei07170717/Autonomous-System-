import time 
import numpy as np
import cv2
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence 
from Body import RobotStateProvider


class Sensor(ABC):
    @abstractmethod
    def get_data(self) -> any: 
        pass

class Camera(Sensor):
    def __init__(
            self):
        pass
        
    def record_video(self):
        pass

    def take_photo(self):
        pass

    def get_data(self):
        pass

class Proprioceptive(Sensor):
    def __init__(self, state: RobotStateProvider):
        self.state = state

    def get_data(self):
        return {
            "joint_angles": self.state.get_joint_angles(),
            "gripper_state": self.state.get_gripper_value()
        }

"""
when defining proprioceptive,
body = MyCobot280PiPhysicalBody(...)
proprio = Proprioceptive(state = body)
"""





