import time 
import numpy as np
import cv2 as cv
import torch
from core.interfaces import ISensor


class Camera(ISensor):
    def __init__(self, id: str, path: str):
        self.path = path
        self.capture = cv.VideoCapture(id)

    def get_tensorized_frame(self):
        """This function will process the frame and turn it into a tensor"""
        does_frame_exist, frame = self.capture.read()
        if does_frame_exist:
            tensorized_frame = self.convert_to_tensor(frame)
            return tensorized_frame
            #cv.imshow('Video Not Resized', frame)# This is just to show the video but isnt needed  
        else:
            raise RuntimeError("Frame doesn't exist")

    def convert_to_tensor(self, frame):
        """This function will convert the frame to a tensor"""
        tensor = torch.from_numpy(frame)
        return tensor

    def get_data(self):
        return self.get_tensorized_frame()
    
    def __del__(self):
        """Making sure the camera resources are released properly."""
        self.capture.release()
        #cv.destroyAllWindows()


"""
when defining proprioceptive,
body = MyCobot280PiPhysicalBody(...)
proprio = Proprioceptive(state = body)
"""





