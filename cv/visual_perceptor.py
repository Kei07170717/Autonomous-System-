import cv2
import numpy as np
from typing import Tuple, Any, Optional


class VisualPerceptor:
    def __init__(self, mm_per_pixel: float = 0.09, debug: bool = False) -> None:
        self._capture = cv2.VideoCapture(0)
        self._capture.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Makes sure only the latest frame can be read
        self.mm_per_pixel = mm_per_pixel
        self.debug = debug
        # Reference origin: assuming the center of a 640x480 camera frame
        self.frame_center_x = 320 
        self.frame_center_y = 240
    
    def set_x_offset(self, x_offset: float):
        self.frame_center_x = 320 + x_offset

    def _get_block_contour(self, block: Any) -> np.ndarray | None:
        ret, frame = self._capture.read()
        if not ret:
            return None

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = block.color
        thresh = block.classification_threshold

        # Bumped min_s up slightly to help reject brown wood
        min_s = 100 
        min_v = 50

        if h - thresh < 0:
            lower1 = np.array([0, min_s, min_v], dtype=np.uint8)
            upper1 = np.array([h + thresh, 255, 255], dtype=np.uint8)
            mask1 = cv2.inRange(hsv, lower1, upper1)
            
            lower2 = np.array([180 + h - thresh, min_s, min_v], dtype=np.uint8)
            upper2 = np.array([179, 255, 255], dtype=np.uint8)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            lower_bound = np.array([max(0, h - thresh), min_s, min_v], dtype=np.uint8)
            upper_bound = np.array([min(179, h + thresh), 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # --- NEW FILTERING LOGIC ---
        valid_contours = []
        for c in contours:
            area = cv2.contourArea(c)
            
            # 1. Size Check
            if not (500 < area < 25000): 
                continue

            # 2. Solidity Check (Is it a solid, convex shape?)
            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull)
            if hull_area == 0:
                continue
            solidity = float(area) / hull_area
            if solidity < 0.85: # A perfect square is 1.0. This rejects jagged shapes.
                continue
            
            # 3. Shape Check (Does it have ~4 corners?)
            peri = cv2.arcLength(c, True)
            # The 0.04 multiplier is the approximation accuracy. 
            # Tweak slightly if it rejects real blocks.
            approx = cv2.approxPolyDP(c, 0.04 * peri, True) 
            if not (3 <= len(approx) <= 5): # Allow 3-5 corners to account for perspective/noise
                continue

            # 4. Aspect Ratio Check
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = float(w) / h
            # A perfect square is 1.0. This allows a little stretching from the camera angle.
            if not (0.7 < aspect_ratio < 1.3): 
                continue

            valid_contours.append(c)
        largest_contour = max(valid_contours, key=cv2.contourArea) if valid_contours else None

        if self.debug:
            debug_frame = frame.copy()
            if largest_contour is not None:
                cv2.drawContours(debug_frame, [largest_contour], -1, (0, 255, 0), 2)
                rect = cv2.minAreaRect(largest_contour)
                box = cv2.boxPoints(rect)
                box = np.int32(box) 
                cv2.drawContours(debug_frame, [box], 0, (0, 0, 255), 1)

            cv2.imshow("Debug: Mask", mask)
            cv2.imshow("Debug: Vision Tracking", debug_frame)
            cv2.waitKey(1) 

        return largest_contour

    def get_block_pos(self, block: Any) -> Tuple[float, float] | None:
        contour = self._get_block_contour(block)
        if contour is None:
            return None

        M = cv2.moments(contour)
        if M["m00"] == 0:
            return None

        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        return cx, cy

    def get_block_orientation(self, block: Any) -> float | None:
        contour = self._get_block_contour(block)
        if contour is None:
            return None

        rect = cv2.minAreaRect(contour)
        angle = rect[2]
        width, height = rect[1]
        
        if width < height:
            angle += 90.0
            
        return angle

    def get_block_length(self, block: Any) -> float | None:
        contour = self._get_block_contour(block)
        if contour is None:
            return None

        rect = cv2.minAreaRect(contour)
        width, height = rect[1]
        
        pixel_length = max(width, height)
        return pixel_length * self.mm_per_pixel

    def get_block_xy_distance(self, block: Any) -> Tuple[float, float] | None:
        pos = self.get_block_pos(block)
        if pos is None:
            return None

        cx, cy = pos
        dx = (cx - self.frame_center_x) * self.mm_per_pixel
        dy = (cy - self.frame_center_y) * self.mm_per_pixel
        
        return dx, dy

    def cleanup(self) -> None:
        """Closes the camera and any open debug windows."""
        self._capture.release()
        if self.debug:
            cv2.destroyAllWindows()
