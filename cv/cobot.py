from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import time

class Cobot:
    def __init__(self) -> None:
        self.mc = MyCobot280(PI_PORT, str(PI_BAUD))
        self.reset_pos()

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
