from typing import Tuple
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import time

_RIGHT_OUTER_BOUND = [200.0, -140.0, 200.0, 180, 0, -45]
_RIGHT_INNER_BOUND = [80.0, -140.0, 200.0, 180, 0, -45]
_LEFT_INNER_BOUND = [80.0, 140.0, 200.0, 180, 0, -45]
_LEFT_OUTER_BOUND = [200.0, 140.0, 200.0, 180, 0, -45]
class Cobot:
    def __init__(self) -> None:
        self.mc = MyCobot280(PI_PORT, str(PI_BAUD))
        self.reset_pos()
        
        # 1. Save a reference to the original, unpatched method
        self._original_send_coords = self.mc.send_coords
        
        # 2. Define your custom override
        def patched_send_coords(coords, speed, mode=1):
            if coords and len(coords) >= 3:
                # Extract x, y, z from whatever was passed in
                x, y, z = coords[0], coords[1], coords[2]
                
                # Append your static rx, ry, rz values
                static_coords = [x, y, z, -180, 0, -45]
                
                # Pass the modified coordinates to the original method
                self._original_send_coords(static_coords, speed, mode)
            else:
                # Fallback just in case malformed data is passed
                self._original_send_coords(coords, speed, mode)
                
        # 3. Replace the library's method with your patched version
        self.mc.send_coords = patched_send_coords

    def reset_pos(self) -> None:
        self.mc.send_coords([110, -63, 205, -180, 0, -45], 5, 1)
        time.sleep(2)

    def set_color(self, r: int, g: int, b: int) -> None:
        self.mc.set_color(r, g, b)

    def descend(self, z_step: float = 20.0, speed: int = 50) -> None:
        coords = self.mc.get_coords()
        if coords:
            coords[2] -= z_step
            self.mc.send_coords(coords, speed, 1)

    def ascend(self, z_step: float = 20.0, speed: int = 50) -> None:
        coords = self.mc.get_coords()
        if coords:
            coords[2] += z_step
            self.mc.send_coords(coords, speed, 1)

    def close_gripper(self, speed: int = 50) -> None:
        self.mc.set_gripper_state(1, speed)

    def open_gripper(self, speed: int = 50) -> None:
        self.mc.set_gripper_state(0, speed)

    def get_z(self) -> float:
        coords = self.mc.get_coords()
        return coords[2] if coords and len(coords) >= 3 else 0.0

    def rotate_eef(self, angle: float, speed: int = 50) -> None:
        self.mc.send_angle(6, angle, speed)

    def stop_moving(self) -> None:
        self.mc.stop()

    def is_moving(self) -> bool:
        return bool(self.mc.is_moving())

    def get_xy(self) -> Tuple[float, float]:
        coords = self.mc.get_coords()

        while coords == -1:
            coords = self.mc.get_coords()
        xy = (float(coords[0]), float(coords[1]))
        return xy


    def set_xyz(self, xyz):
        success = self.mc.send_coords([xyz[0], xyz[1], xyz[2], 0, 0, 0], 1, 1)
        while success == -1:
            success = self.mc.send_coords([xyz[0], xyz[1], xyz[2], 0, 0, 0], 1, 1)


