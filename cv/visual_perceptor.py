import cv2
import numpy as np
from typing import Tuple, Any, Optional

class VisualPerceptor:
    def __init__(self, mm_per_pixel: float = 1.0, debug: bool = False) -> None:
        self._capture = cv2.VideoCapture(0)
        self.mm_per_pixel = mm_per_pixel
        self.debug = debug
        # Reference origin: assuming the center of a 640x480 camera frame
        self.frame_center_x = 320 
        self.frame_center_y = 240

    def _get_block_contour(self, block: Any) -> Optional[np.ndarray]:
        ret, frame = self._capture.read()
        if not ret:
            return None

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = block.color
        thresh = block.classification_threshold

        lower_bound = np.array([max(0, h - thresh), max(0, s - 50), max(0, v - 50)])
        upper_bound = np.array([min(179, h + thresh), 255, 255])

        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best_contour = max(contours, key=cv2.contourArea) if contours else None

        # --- DEBUG VISUALIZATION ---
        if self.debug:
            debug_frame = frame.copy()
            if best_contour is not None:
                # 1. Draw the exact contour shape (Green)
                cv2.drawContours(debug_frame, [best_contour], -1, (0, 255, 0), 2)
                
                # 2. Draw the minimum area bounding box (Red)
                rect = cv2.minAreaRect(best_contour)
                box = cv2.boxPoints(rect)
                box = np.int32(box) 
                cv2.drawContours(debug_frame, [box], 0, (0, 0, 255), 2)
                
                # 3. Draw the centroid (Blue)
                M = cv2.moments(best_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(debug_frame, (cx, cy), 5, (255, 0, 0), -1)

            # Display the windows
            cv2.imshow("Vision Debug - Camera Feed", debug_frame)
            cv2.imshow("Vision Debug - HSV Mask", mask)
            
            # cv2.waitKey(1) is strictly required to force OpenCV to render and refresh the GUI
            cv2.waitKey(1) 
        # ---------------------------

        return best_contour

    def get_block_pos(self, block: Any) -> Tuple[float, float]:
        contour = self._get_block_contour(block)
        if contour is None:
            return 0.0, 0.0

        M = cv2.moments(contour)
        if M["m00"] == 0:
            return 0.0, 0.0

        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        return cx, cy

    def get_block_orientation(self, block: Any) -> float:
        contour = self._get_block_contour(block)
        if contour is None:
            return 0.0

        rect = cv2.minAreaRect(contour)
        angle = rect[2]
        width, height = rect[1]
        
        if width < height:
            angle += 90.0
            
        return angle

    def get_block_length(self, block: Any) -> float:
        contour = self._get_block_contour(block)
        if contour is None:
            return 0.0

        rect = cv2.minAreaRect(contour)
        width, height = rect[1]
        
        pixel_length = max(width, height)
        return pixel_length * self.mm_per_pixel

    def get_block_xy_distance(self, block: Any) -> Tuple[float, float]:
        cx, cy = self.get_block_pos(block)
        if cx == 0.0 and cy == 0.0:
            return 0.0, 0.0

        dx = (cx - self.frame_center_x) * self.mm_per_pixel
        dy = (cy - self.frame_center_y) * self.mm_per_pixel
        
        return dx, dy
