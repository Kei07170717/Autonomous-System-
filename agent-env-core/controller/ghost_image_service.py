import cv2
import time
import threading
import numpy as np
from flask import Flask, Response
from werkzeug.serving import make_server
from abc import ABC

# Assuming ICameraSensor is imported from your core.interfaces
# from core.interfaces import ICameraSensor
# from your_camera_file import FrameNotReadyError, NullFrameReturnedError

class IGhostImageServer(ABC):
    def start(self):
        pass

    def stop(self):
        pass
    
    def take_ref(self):
        pass

class GhostImageServer(IGhostImageServer):
    def __init__(self, camera, ref_image_path: str = "reference_frame.jpg", host: str = '0.0.0.0', port: int = 5000):
        """
        Serves a video feed over html. Usefull for monitoring but does 
        take up resources. Best to use during Idling state.
        """
        self.camera = camera
        self.ref_image_path = ref_image_path
        self.host = host
        self.port = port
        
        self.reference_img = None
        self._load_ref()
        self.old_res = None  # Resolution before increasing
        self.old_is_resize_center_crop_enabled = None

        # Set up Flask app
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'video_feed', self.video_feed)
        
        # Threading and Server control
        self.server = None
        self.server_thread = None
        self.is_running = threading.Event()

    def _load_ref(self):
        """Try to load the reference image on boot."""
        img = cv2.imread(self.ref_image_path)
        if img is not None:
            self.reference_img = img
        else:
            print(f"Notice: No reference image found at {self.ref_image_path}. Run take_ref() first.")

    def take_ref(self):
        """
        Grabs the current frame from the running Camera instance, 
        saves it to disk, and updates the active ghost overlay.
        """
        try:
            frame = self.camera.get_current_frame()
            cv2.imwrite(self.ref_image_path, frame)
            self.reference_img = frame
            # print(f"Success: Reference image saved to '{self.ref_image_path}'.")
        except Exception as e:
            print(f"Error taking reference frame: {e}")

    def generate_frames(self):
        """Generator that continuously yields blended frames to the web browser."""
        while self.is_running.is_set():
            try:
                # Ask your existing Camera thread for a copy of the latest frame
                frame = self.camera.get_current_frame()
                
                if self.reference_img is not None:
                    # Failsafe: Resize if the camera resolution changed since taking the ref photo
                    if frame.shape != self.reference_img.shape:
                        frame = cv2.resize(frame, (self.reference_img.shape[1], self.reference_img.shape[0]))
                    
                    # 50/50 blend
                    blended = cv2.addWeighted(frame, 0.5, self.reference_img, 0.5, 0)
                else:
                    blended = frame
                
                blended = add_square_overlay(blended)
                # Encode to JPEG
                ret, buffer = cv2.imencode('.jpg', blended)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                       
                # Cap the stream at roughly ~30fps to save CPU overhead
                time.sleep(0.03) 

            except Exception:
                # Catches FrameNotReadyError or NullFrameReturnedError from your Camera class
                # Sleeps briefly to prevent a tight loop if the camera drops momentarily
                time.sleep(0.1) 

    def video_feed(self):
        """Flask route handler"""
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def start(self):
        """Boots the Flask server and switches the camera to High Resolution."""
        if self.is_running.is_set():
            print("Ghost server is already running.")
            return

        self.old_res = self.camera.get_actual_resolution()
        self.old_is_resize_center_crop_enabled = self.camera.get_resize_center_crop()
        self.camera.set_to_rgb(False)
        self.camera.set_resize_center_crop(False)
        self.camera.change_resolution(1920, 1080)

        self.is_running.set()
        self.server = make_server(self.host, self.port, self.app)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        print(f"Ghost Image Server started at http://{self.host}:{self.port}")

    def stop(self):
        """Shuts down the server and reverts the camera to previously set resolution."""
        if not self.is_running.is_set():
            return

        print("Shutting down Ghost Image Server...")
        self.is_running.clear()
        
        if self.server:
            self.server.shutdown()
            self.server_thread.join()
        
        self.camera.set_to_rgb(True)
        if self.old_is_resize_center_crop_enabled is True:
            self.camera.set_resize_center_crop(True)
        if self.old_res:
            self.camera.change_resolution(self.old_res["width"], self.old_res["height"])
            

def add_square_overlay(frame, color=(0, 255, 0), thickness=2):
    """
    Calculates the center square of a frame and draws it.
    Returns the frame with the overlay.
    """
    height, width = frame.shape[:2]
    
    # Calculate the side length (shortest dimension)
    size = min(width, height)
    
    # Calculate coordinates for centering
    start_x = (width - size) // 2
    start_y = (height - size) // 2
    end_x = start_x + size
    end_y = start_y + size
    
    # Draw the rectangle on a copy to keep the original clean if needed
    # Use frame.copy() if you don't want to modify the input frame in place
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), color, thickness)
    
    return frame
