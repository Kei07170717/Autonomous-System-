import cv2 
from cv2_enumerate_cameras import enumerate_cameras
from numpy._typing import NDArray
import torch
import platform
import threading
from torch import Tensor

from core.interfaces import ICameraSensor


class FrameNotReadyError(Exception):
    """Raised when a frame is requested before it exists."""
    pass

class NullFrameReturnedError(Exception):
    """Raised when an empty/null frame is read."""
    pass

class Camera(ICameraSensor):
    """
    This class gets as input the camera name(example names are in get_camera_path docstring) 
    and returns either the actual frame or a tensorized version of the frame
    """
    def __init__(self, camera_name: str):
        self.camera_name: str = camera_name
        self.path: int = self.get_camera_path()
        self.capture = cv2.VideoCapture(self.path)
        self.latest_frame = None
        self.capture_failed = False
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()
    
    def get_camera_path(self) -> int:
        """
        Finding the correct camera to start the thread in the correct index
        Corrrect Camera names:
        USB 2.0 Camera ~ wrist camera from robot arm
        USB Camera ~ Bartinos camera
        FaceTime HD Camera ~ any macbook face camera
        """
        
        def get_os():
            """
            Autodetect which OS is being used  -> important for the detection of the camera name / index.
            Different os have different backend values to access for camera 
            """
            if platform.system() == 'Darwin':
                backend = cv2.CAP_AVFOUNDATION  #mac
            elif platform.system() == 'Windows':
                backend = cv2.CAP_MSMF #windows
            else:
                backend = cv2.CAP_V4L2 #linux
            return backend

        cams: list = enumerate_cameras(get_os()) 
        for cam in cams:
            if cam.name.lower() == self.camera_name.lower():
                return cam.index
        raise ValueError("Camera could not be found for use")
    
    def update_frames(self):
        """Continuously grab frames for the thread"""
        while not self.stop_event.is_set(): 
            does_frame_exist, frame = self.capture.read()
            
            if not does_frame_exist:
                self.running = False
                self.capture_failed = True
                # raise NullFrameReturnedError("Frame does not exist, exiting cam thread")
                break
            with self.lock:
                self.latest_frame = frame
    
    def get_current_frame(self) -> NDArray:
        """Return the latest frame read by the camera thread."""
        with self.lock:
            # Check for permanent failure first
            if self.capture_failed:
                raise NullFrameReturnedError("Frame does not exist, background capture failed")
                
            # Then check if we are just waiting for the first frame
            if self.latest_frame is None:
                raise FrameNotReadyError("Frame doesn't exist yet")

            return self.latest_frame.copy()

    

    def get_current_frame_as_tensor(self) -> Tensor:
        """This function will process the frame and turn it into a tensor"""
        frame = self.get_current_frame()
        
        def convert_to_tensor(frame) -> Tensor:
            """This function converts each frame to a tensor"""
            return torch.from_numpy(frame)

        return convert_to_tensor(frame)
        
    
    def stop(self):
        """Stop the camera thread and release the camera."""
        self.stop_event.set()
        if self.thread.is_alive():
            self.thread.join()

        # Explicitly release the OpenCV resource
        if self.capture.isOpened():
            self.capture.release()

    # TODO: Apparently shouldn't rely on destructor, likely causing the core dump
    def __del__(self):
        """Making sure the camera resources are released properly."""
        try:
            self.stop()
        except Exception as e:
            pass






