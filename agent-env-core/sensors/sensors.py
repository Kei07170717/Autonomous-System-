import time 
import numpy as np
import cv2
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence 
from body import RobotStateProvider


class Sensor(ABC): 
    '''
    Sensor based class
    '''
    def __init__(self, id: str):
        self.id: str = id

    def get_id(self):
        return self.id

    @abstractmethod
    def get_data(self) -> any: 
        pass

class Camera(Sensor):
    def __init__(
            self,
            id: str):
        super().__init__(self, id = id)
        
    def get_data(self):
        pass

class Proprioceptive(Sensor):
    def __init__(
            self, 
            id: str, 
            state: RobotStateProvider):
        
        super().__init__(self, id=id)
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





