import time 
import numpy as np
import cv2 as cv
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence
import torch
from core.interfaces import ISensor
# from body import RobotStateProvider


class Camera(ISensor):
    def __init__(self, id: str, path: str):
        self.path = path
        self.capture = cv.VideoCapture(id)

    def get_tensorized_frame(self):
        """This function will process the frame and turn it into a tensor"""
        does_frame_exist, frame = self.capture.read()
        if does_frame_exist:
            tensorized_frame=self.convert_to_tensor(frame)
            return tensorized_frame
            #cv.imshow('Video Not Resized', frame)# This is just to show the video but isnt needed  
        else:
            raise RuntimeError("Frame doesn't exist")

    def convert_to_tensor(self,frame):
        """This function will convert the frame to a tensor"""
        tensor=torch.from_numpy(frame)
        return tensor

    def get_data(self):
        return self.get_tensorized_frame()
    
    def __del__(self):
        """Making sure the camera resources are released properly."""
        self.capture.release()
        #cv.destroyAllWindows()


# class Proprioceptive(Sensor):
#     def __init__(
#             self, 
#             id: str, 
#             state: RobotStateProvider):
#
#         super().__init__(self, id=id)
#         self.state = state
#
#     def get_data(self):
#         return {
#             "joint_angles": self.state.get_joint_angles(),
#             "gripper_state": self.state.get_gripper_value()
#         }

"""
when defining proprioceptive,
body = MyCobot280PiPhysicalBody(...)
proprio = Proprioceptive(state = body)
"""





