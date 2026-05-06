from typing import Tuple
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import time
import math

_RIGHT_OUTER_BOUND = [200.0, -140.0, 200.0, 180, 0, -45]
_RIGHT_INNER_BOUND = [80.0, -140.0, 200.0, 180, 0, -45]
_LEFT_INNER_BOUND = [80.0, 140.0, 200.0, 180, 0, -45]
_LEFT_OUTER_BOUND = [200.0, 140.0, 200.0, 180, 0, -45]
_MIN_X, _MAX_X = 80.0, 200.0
_MIN_Y, _MAX_Y = -140.0, 140.0
_MIN_Z, _MAX_Z = 100.0, 200.0
class Cobot:
    def __init__(self) -> None:
        self.mc = MyCobot280(PI_PORT, str(PI_BAUD))
        self.current_eef_angle = -45
        self.current_z_rotation = -45
        self.current_z = 200.0
        self.reset_pos()
        
        # 1. Save a reference to the original, unpatched method
        self._original_send_coords = self.mc.send_coords
        
        # 2. Define your custom override
        def patched_send_coords(coords, speed, mode=1):
            if coords and len(coords) >= 3:
                # Extract x, y, z from whatever was passed in
                x, y, z = coords[0], coords[1], coords[2]
               
                
                print(f"SELF Z ROTATION: {self.current_z_rotation}")

                static_coords = [x, y, self.current_z, -180, 0, self.current_z_rotation]
                # print(f"SELF Z ROTATION: {self.current_z_rotation}")
                
                # Pass the modified coordinates to the original method
                self._original_send_coords(static_coords, speed, mode)
            else:
                # Fallback just in case malformed data is passed
                print("Patch ignored")
                self._original_send_coords(coords, speed, mode)
                
        # 3. Replace the library's method with your patched version
        self.mc.send_coords = patched_send_coords

    def reset_pos(self) -> None:

        self.current_eef_angle = -45
        success = self.mc.send_coords([110, -63, 205, -180, 0, self.current_z_rotation], 5, 1)
        while success == -1:
            print("Failed to reset pos")
            success = self.mc.send_coords([110, -63, 205, -180, 0, self.current_z_rotation], 5, 1)


        time.sleep(2)

    def set_color(self, rgb_value: tuple) -> None:
        self.mc.set_color(rgb_value[0], rgb_value[1], rgb_value[2])

    def descend(self, z_step: float = 5.0, speed: int = 50) -> None:
        new_z = max(self.current_z - z_step, _MIN_Z)
        success = self.mc.send_coord(3, new_z, speed)
        while success == -1:
            success = self.mc.send_coord(3, new_z, speed)

        self.current_z = new_z


    # def ascend(self, z_step: float = 20.0, speed: int = 50) -> None:
    #     new_z = max(self.current_z + z_step, _MIN_Z)
    #     success = self.mc.send_coord(3, new_z, speed)
    #     while success == -1:
    #         success = self.mc.send_coord(3, new_z, speed)
    #
    #     self.current_z = new_z

    def close_gripper(self, speed: int = 100) -> None:
        success = self.mc.set_gripper_state(1, speed)
        while success == -1:
            success = self.mc.set_gripper_state(1, speed)
        self.wait_for_gripper_movement_completion()

    def open_gripper(self, speed: int = 50) -> None:
        success =self.mc.set_gripper_state(0, speed)
        while success == -1:
            success =self.mc.set_gripper_state(0, speed)
        self.wait_for_gripper_movement_completion()

    def get_z(self) -> float:
        coords = self.mc.get_coords()
        return coords[2] if coords and len(coords) >= 3 else 0.0

    def rotate_eef(self, angle: float, speed: int = 100) -> None:
        print(f"Applying {angle} to current rotation {self.current_z_rotation}")
        new_z_rotation = self.current_z_rotation - angle
        success = self.mc.send_coord(6, new_z_rotation, speed)
        while success == -1:
            print("Rotation set failed")
            success = self.mc.send_coord(6, new_z_rotation, speed)
        # self.current_eef_angle = new_z_rotation
        self.wait_for_navigation_completion()
        # time.sleep(1)

        # coords = self.mc.get_coords()
        # while coords == -1:
        #     coords = self.mc.get_coords()
        # read_z_rotation = coords[5]

        # print(f"Setting current_z_rotation ({self.current_z_rotation}) to {read_z_rotation}")
        print(f"Setting current_z_rotation ({self.current_z_rotation}) to {new_z_rotation}")
        self.current_z_rotation = new_z_rotation


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



    # def set_xyz(self, xyz):
    #     success = self.mc.send_coords([xyz[0], xyz[1], xyz[2], 0, 0, 0], 1, 1)
    #     while success == -1:
    #         success = self.mc.send_coords([xyz[0], xyz[1], xyz[2], 0, 0, 0], 1, 1)
    
    def set_xyz(self, xyz, speed: int = 30):
        clamped_x = max(_MIN_X, min(xyz[0], _MAX_X))
        clamped_y = max(_MIN_Y, min(xyz[1], _MAX_Y))
        clamped_z = max(_MIN_Z, min(xyz[2], _MAX_Z))

        # Use the clamped values for the movement command
        success = self.mc.send_coords([clamped_x, clamped_y, clamped_z, 0, 0, 0], speed, 1)
        
        while success == -1:
            print("Retrying set_xyz")
            success = self.mc.send_coords([clamped_x, clamped_y, clamped_z, 0, 0, 0], speed, 1)
    
    def set_z(self, z: float, speed: int = 50):
        clamped_z = max(_MIN_Z, min(z, _MAX_Z))

        # Use the clamped values for the movement command
        success = self.mc.send_coord(3, clamped_z, speed)
        
        while success == -1:
            success = self.mc.send_coord(3, clamped_z, speed)

        self.current_z = clamped_z


    def wait_for_navigation_completion(self):
        while self.is_moving():
            print("Waiting for nav completion...")
            time.sleep(0.1)


    def wait_for_gripper_movement_completion(self):
        # while self.mc.is_gripper_moving() != 0: # Often gets stuck
        #     print("Waiting for gripper completion...")
        #     time.sleep(0.2)
        time.sleep(2)

    def get_relative_z_rotation(self) -> float:
        return self.current_z_rotation + 45
