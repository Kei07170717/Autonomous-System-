import cv2 
from cv2_enumerate_cameras import enumerate_cameras
import torch
import platform
import threading
from torch import Tensor


class Camera:
    """
    This class gets as input the camera name(example names are in get_camera_path docstring) 
    and returns either the actual frame or a tensorized version of the frame
    """
    def __init__(self, camera_name: str):
        self.camera_name: str = camera_name
        self.path: int = self.get_camera_path()
        self.capture = cv2.VideoCapture(self.path)
        self.latest_frame = None
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
                print("Frame does not exist exiting update_frames")
                break
            with self.lock:
                self.latest_frame = frame
    
    def get_current_frame(self):
        """Return the latest frame read by the background thread.
        returns the actual frame and not the tensor so might not be needed in the future
        """
        with self.lock:
            if self.latest_frame is None:
                return None
            return self.latest_frame.copy()
    

    def get_tensorized_frame(self) -> Tensor:
        """This function will process the frame and turn it into a tensor"""
        frame = self.get_current_frame()
        
        def convert_to_tensor(frame) -> Tensor:
            """This function converts each frame to a tensor"""
            return torch.from_numpy(frame)
        
        if frame is not None:
            tensorized_frame: Tensor = convert_to_tensor(frame)
            return tensorized_frame
        else:
            raise RuntimeError("Frame doesn't exist")
    
    def stop(self):
        """Stop the camera thread and release the camera."""
        self.stop_event.set()
        if self.thread.is_alive():
            self.thread.join()
    
    def __del__(self):
        """Making sure the camera resources are released properly."""
        self.stop()






