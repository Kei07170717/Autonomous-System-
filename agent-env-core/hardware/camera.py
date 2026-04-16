import cv2 
from cv2_enumerate_cameras import enumerate_cameras
from numpy._typing import NDArray
import torch
import platform
import threading
from torch import Tensor
import time
from core.interfaces import ICameraSensor


class FrameNotReadyError(Exception):
    """Raised when a frame is requested before it exists."""
    pass

class NullFrameReturnedError(Exception):
    """Raised when an empty/null frame is read."""
    pass

# Globals because setting them as params is too tricky; 
# if someone changes these, it must be communicated with the team!
# Having this changed between demonstrations in the dataset can cause problems
_RES_WIDTH = 352 
_RES_HEIGHT = 288
_TARGET_FPS = 30
class Camera(ICameraSensor):
    """
    This class gets as input the camera name(example names are in get_camera_path docstring) 
    and returns either the actual frame or a tensorized version of the frame.
    Camera class should be modified with care as transformation of the frames should be 
    the same during gathering demonstrations and inference. 
    """
    def __init__(self, camera_name: str):
        self.camera_name: str = camera_name
        self.os: int = self._get_os()
        self.path: int = self.get_camera_path()
        self.capture = cv2.VideoCapture(self.path, self.os)
                
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, _RES_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, _RES_HEIGHT)
        self.capture.set(cv2.CAP_PROP_FPS, _TARGET_FPS)

        try:
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Makes sure only the latest frame can be read (probably not necessary)
        except Exception:
            print(f"Warning: couldn't set camera buffer to 1 frame for cam: {camera_name}")

        if not self._verify_set_res_and_fps():
            print(f"Warning: actual camera resolution or FPS do not match set target for cam: {self.camera_name}")

        self.latest_frame = None
        self.capture_failed = False
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()
        
    def _get_os(self):
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
    
    def get_camera_path(self) -> int:
        """
        Finding the correct camera to start the thread in the correct index
        Corrrect Camera names:
        USB 2.0 Camera ~ wrist camera from robot arm
        USB Camera ~ Bartinos camera
        FaceTime HD Camera ~ any macbook face camera
        """
        

        cams: list = enumerate_cameras(self.os) 
        for cam in cams:
            if self.camera_name.lower() == cam.name.lower():
                
                # Test the index before returning it
                test_cap = cv2.VideoCapture(cam.index, self.os)
                if test_cap.isOpened():
                    success, _ = test_cap.read()
                    test_cap.release()
                    
                    if success:
                        return cam.index
                    else:
                        print(f"Warning: Index {cam.index} matched name but failed to read a frame. Trying next...")
                else:
                    print(f"Warning: Index {cam.index} matched but failed to open.")

        raise ValueError(f"Camera '{self.camera_name}' could not be found or opened for use.")
   
    def _verify_set_res_and_fps(self):
        actual_w = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.capture.get(cv2.CAP_PROP_FPS)

        if actual_h != _RES_HEIGHT or actual_w != _RES_WIDTH or actual_fps != _TARGET_FPS:
            return False
        return True

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


    def change_resolution(self, width: int, height: int):
        """Safely restart the camera feed with a new resolution."""
        print(f"Switching camera '{self.camera_name}' resolution to {width}x{height}...")
        
        # 1. Stop the background reading thread
        self.stop_event.set()
        if self.thread.is_alive():
            self.thread.join()
            
        # 2. Release the hardware lock
        if self.capture.isOpened():
            self.capture.release()
            
        # 3. Re-initialize the capture with the new resolution
        self.capture = cv2.VideoCapture(self.path, self.os)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.capture.set(cv2.CAP_PROP_FPS, _TARGET_FPS)
        
        try:
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        # 4. Reset state and restart the background thread
        self.latest_frame = None
        self.capture_failed = False
        self.stop_event.clear()
        
        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()

        # Wait for the first frame to arrive before returning
        timeout = 5.0 
        start_time = time.time()
        while self.latest_frame is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            
        if self.latest_frame is None:
            raise FrameNotReadyError(f"Camera failed to provide a frame at {width}x{height} within timeout.")

        print(f"Resolution switch complete for '{self.camera_name}'.")
        
    
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






