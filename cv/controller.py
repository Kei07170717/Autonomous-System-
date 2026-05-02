
from typing import Tuple

from cv2 import threshold
from block import Block
from cobot import Cobot
from util import stable_bool
from visual_perceptor import VisualPerceptor
import time

_OVERVIEW_HEIGHT = 200

class StackController():
    
    def __init__(self, cobot: Cobot, visual_perceptor: VisualPerceptor) -> None:
        self.cobot = cobot
        self.vp = visual_perceptor
        blue_block = Block(color=(120, 255, 255), classification_threshold=15.0)
        red_block = Block(color=(0, 255, 255), classification_threshold=10.0)
        self.top_block: Block = red_block
        self.bottom_block: Block = blue_block
        self.operating_height = _OVERVIEW_HEIGHT

    def start(self):
        strat = self._locate_top_block
        while strat != None:
            strat = strat()

    def _locate_top_block(self):
        self.operating_height = _OVERVIEW_HEIGHT
        self.cobot.open_gripper()

        block_pos = self.vp.get_block_pos(self.top_block)

        while block_pos is None:
            self._explore_space()
            block_pos = self.vp.get_block_pos(self.top_block)

        self.cobot.stop_moving()

        while not self._is_xy_aligned(current_xy = block_pos):
            time.sleep(0.5)
            new_block_pos = self.vp.get_block_xy_distance(self.top_block)
            block_pos = new_block_pos if new_block_pos is not None else block_pos
            self.correct_xy_position(block_pos[0], -block_pos[1])
            print(f"Block pos: {block_pos}")


    def _grab_top_block(self):
        return None
    
    def _locate_bottom_block(self):
        return None

    def _stack_top_block(self):
        return None

    def _explore_space(self):
        pass

    # def _is_xy_aligned(self, current_xy: Tuple[float, float], target_xy: Tuple[float, float], threshold: float=10) -> bool:
    #     return (target_xy[0] - current_xy[0]) < threshold and  (target_xy[1] - current_xy[1]) < threshold

    @stable_bool(threshold=5)
    def _is_xy_aligned(self, current_xy: Tuple[float, float], target_xy: Tuple[float, float] = (0, 0), threshold: float=30) -> bool:

        aligned = abs(target_xy[0] - current_xy[0]) < threshold and abs(target_xy[1] - current_xy[1]) < threshold
        # print(f"Tar: {aligned}")
        print(f"Aligned: {aligned}")
        return aligned
        
    def correct_xy_position(self, delta_x: float, delta_y: float) -> None:
        current_xy = self.cobot.get_xy()
        target_coords = [
            current_xy[0] + delta_x,
            current_xy[1] + delta_y
        ]
        
        # Send the new coordinates back to the arm
        # print(f"Corrective coords: {coords}")
        self.cobot.set_xyz((target_coords[0], target_coords[1], self.operating_height))
