
from typing import Tuple

from cv2 import threshold
from block import Block
from cobot import _RIGHT_INNER_BOUND, _RIGHT_OUTER_BOUND, _LEFT_OUTER_BOUND, _LEFT_INNER_BOUND, Cobot
from util import rotate_point, stable_bool
from visual_perceptor import VisualPerceptor
import time
import itertools

_OVERVIEW_HEIGHT = 200
_GRABBING_HEIGHT = 135
_STACKING_HEIGHT = 175
_STACKED_BLOCK_THRESHOLD = 11
_LOST_BLOCK_THRESHOLD = 5

_DESCEND_RATE = 5

_EXPLORATION_COORDS = [_RIGHT_INNER_BOUND, _RIGHT_OUTER_BOUND, _LEFT_OUTER_BOUND, _LEFT_INNER_BOUND]
_COORD_ITERATOR = itertools.cycle(_EXPLORATION_COORDS)
_TOP_BLOCK_ALIGNMENT_OFFSET = -100
_BOTTOM_BLOCK_ALIGNMENT_OFFSET = 0
_STACK_TOP_BLOCK_ALIGNMENT_OFSSET = -200

PURPLE = (160, 32, 240)
GREEN = (0, 128, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0,0,255)

class LostBlockError(Exception):
    pass

class StackController():
    
    def __init__(self, cobot: Cobot, visual_perceptor: VisualPerceptor) -> None:
        self.cobot = cobot
        self.vp = visual_perceptor
        blue_block = Block(color=(120, 255, 255), classification_threshold=15.0)
        red_block = Block(color=(0, 255, 255), classification_threshold=10.0)
        self.top_block: Block = blue_block
        self.bottom_block: Block = red_block
        
        self.operating_height = _OVERVIEW_HEIGHT
        self.vp.set_x_offset(_TOP_BLOCK_ALIGNMENT_OFFSET)
        
    
    def set_state_color(self, state,):
        if state == "start" or state == "Found":
            self.cobot.set_color(GREEN)
        if state == self.bottom_block: # looking for bottom block
            self.cobot.set_color(RED)
        if state == self.top_block:
            self.cobot.set_color(BLUE)
        if state == "end" or state == "idle":
            self.cobot.set_color(PURPLE)
        if state == "failed":
            self.cobot.set_color(WHITE)
            
            

    def start(self):
        strat = self._locate_top_block
        self.set_state_color("start") #set color to green when starting
        while strat != None:
            strat = strat()

    def _locate_top_block(self):
        print("Entered locate top block strat")
        self.vp.set_x_offset(_TOP_BLOCK_ALIGNMENT_OFFSET)
        self.operating_height = _OVERVIEW_HEIGHT
        self.cobot.set_z(self.operating_height)
        # self.cobot.reset_pos()
        self.cobot.open_gripper()

        block_pos = self.vp.get_block_pos(self.top_block)
        self.set_state_color(self.top_block)# set color to that of top block while looking for that color
        while block_pos is None:
            if not self.cobot.is_moving():

                self._explore_space()
            block_pos = self.vp.get_block_pos(self.top_block)
            

        self.cobot.stop_moving()

        try:
            self._align_xy(self.top_block) 
        except LostBlockError as e:
            print("Lost block while locating top block")
            return self._locate_top_block
        
        if self._is_block_stacked(): 
            print("Blocks are already stacked...")
            self.cobot.set_color("idle")
            return self._locate_top_block
        else:
            self.set_state_color("found") #change the display to green
            return self._grab_top_block



    def _grab_top_block(self):
        print("Entered grab top block strat")
        self.vp.set_x_offset(_TOP_BLOCK_ALIGNMENT_OFFSET)
         
        self._match_rotation(self.top_block)
        
        block_pos = self.vp.get_block_pos(self.top_block)
        
        if block_pos is None:
            return self._locate_top_block
       
        while True:
            time.sleep(0.2)
            block_pos = self.vp.get_block_pos(self.top_block)
            if not self._is_xy_aligned(block_pos):
                self._align_xy(self.top_block)
                block_pos = self.vp.get_block_pos(self.top_block)

            if abs(_GRABBING_HEIGHT - self.operating_height) <= 3:
                
                self._align_xy(self.top_block, threshold=1)
                self.cobot.close_gripper()
                return self._locate_bottom_block
                
            self.cobot.descend(_DESCEND_RATE, 1)
            
            while self.cobot.is_moving():
                time.sleep(0.1)
            self.operating_height -= _DESCEND_RATE
            # break


        
        return None
    
    def _locate_bottom_block(self):
        print("Entered locate bottom block strat")
        self.set_state_color(self.bottom_block) # Color of bottom block
        self.vp.set_x_offset(_BOTTOM_BLOCK_ALIGNMENT_OFFSET)
        self.operating_height = _OVERVIEW_HEIGHT
        self.cobot.set_z(self.operating_height, 100)
        time.sleep(0.5)
        self.cobot.wait_for_navigation_completion()

        block_pos = self.vp.get_block_pos(self.bottom_block)
        

        while block_pos is None:
            if not self.cobot.is_moving():
                self._explore_space()
            block_pos = self.vp.get_block_pos(self.bottom_block)

        self.cobot.stop_moving()
        
        try:
            self._align_xy(self.bottom_block) 
        except LostBlockError as e:
            self.set_state_color("failed")
            print("Warning: ", e)
            return self._locate_bottom_block
        self.set_state_color("found")
        return self._stack_top_block

    def _stack_top_block(self):
        print("Entered stack top block strat")
        self.vp.set_x_offset(_BOTTOM_BLOCK_ALIGNMENT_OFFSET)
        self._match_rotation(self.bottom_block)
        self._align_xy(self.bottom_block)
        
        recovery_attempts_allowed = 2
        recovery_count = 0
        while True:
            try:
                block_pos = self._get_block_delta_pos_or_panic(self.bottom_block)
            except LostBlockError as e:
                print("Lost block while aliging for stacking")
                # if recovery_count == recovery_attempts_allowed:
                self.set_state_color("failed")
                return self._locate_bottom_block
                # else:
                #     recovery_count += 1
                    # ???

                
            if not self._is_xy_aligned(block_pos):
                try:
                    self._align_xy(self.bottom_block) 
                except LostBlockError as e:
                    print("Warning: ", e)
                    return self._locate_bottom_block
                block_pos = self.vp.get_block_pos(self.bottom_block)

            if abs(_STACKING_HEIGHT - self.operating_height) <= 3:
                self._align_xy(self.bottom_block, threshold=1)
                self.vp.set_x_offset(_STACK_TOP_BLOCK_ALIGNMENT_OFSSET)
                block_pos = self._get_block_delta_pos_or_panic(self.bottom_block)
                print(f"FINAL BLOCK POS: {block_pos}")
                time.sleep(1)
                self.correct_xy_position(block_pos[0], block_pos[1], self.cobot.get_relative_z_rotation())
                time.sleep(1)
                self.cobot.wait_for_navigation_completion()
                self.cobot.open_gripper(100)
                return self._locate_top_block
                
            self.cobot.descend(_DESCEND_RATE, 1)
            while self.cobot.is_moving():
                time.sleep(0.1)
            self.operating_height -= _DESCEND_RATE
            time.sleep(0.2)
        return None

    def _get_block_delta_pos_or_panic(self, block: Block, panic_threshold: int = 3):
        lost_count = 0
        while True:
            block_pos = self.vp.get_block_xy_distance(block, self.cobot.get_relative_z_rotation())
            if block_pos is not None:
                return block_pos
            
            lost_count += 1
            if lost_count >= panic_threshold:
                self.set_state_color("failed")
                raise LostBlockError("Lost block")

    def _explore_space(self):
        self.cobot.set_xyz(next(_COORD_ITERATOR), speed=50)

    def _match_rotation(self, block: Block):
        rotation = self.vp.get_block_orientation(block)
        if rotation is not None:
            self.cobot.rotate_eef(rotation)
        print(f"Block orientation: {rotation}")

    def _align_xy(self, target_block: Block, threshold: float=3):
        lost_count = 0
        block_pos = self.vp.get_block_xy_distance(target_block)
        while block_pos is None:
            block_pos = self.vp.get_block_xy_distance(target_block)
            lost_count += 1
            if lost_count >= _LOST_BLOCK_THRESHOLD:
                self.set_state_color("failed")
                raise LostBlockError("Lost block while aligning")


        lost_count = 0
        while not self._is_xy_aligned(current_xy = block_pos, threshold=threshold):
            time.sleep(0.1)
            new_block_pos = self.vp.get_block_xy_distance(target_block)
            if new_block_pos is not None:
                block_pos = new_block_pos
                self.correct_xy_position(block_pos[0], -block_pos[1], self.cobot.get_relative_z_rotation())
                lost_count = 0
            else:
                lost_count += 1
                print(f"Lost block count: {lost_count}")
                if lost_count >= _LOST_BLOCK_THRESHOLD:
                    self.set_state_color("failed")
                    raise LostBlockError("Lost block while aligning")
                
            
            print(f"Block pos: {block_pos}")

    # def _is_xy_aligned(self, current_xy: Tuple[float, float], target_xy: Tuple[float, float], threshold: float=10) -> bool:
    #     return (target_xy[0] - current_xy[0]) < threshold and  (target_xy[1] - current_xy[1]) < threshold

    @stable_bool(threshold=1)
    def _is_xy_aligned(self, current_xy: Tuple[float, float], target_xy: Tuple[float, float] = (0, 0), threshold: float=3) -> bool:

        aligned = abs(target_xy[0] - current_xy[0]) < threshold and abs(target_xy[1] - current_xy[1]) < threshold
        # print(f"Tar: {aligned}")
        print(f"Aligned: {aligned}")
        return aligned
        
    def correct_xy_position(self, delta_x: float, delta_y: float, rot_degree: float = 0) -> None:
        current_xy = self.cobot.get_xy()
        if rot_degree != 0:
            delta_x, delta_y = rotate_point(delta_x, delta_y, rot_degree)
        target_coords = [
            current_xy[0] + delta_x,
            current_xy[1] + delta_y
        ]       
        
        # Send the new coordinates back to the arm
        # print(f"Corrective coords: {coords}")
        self.cobot.set_xyz((target_coords[0], target_coords[1], self.operating_height))

    def _is_block_stacked(self, certainty_count: int = 3) -> bool:
        is_stacked_count = 0 

        # is_stacked_list = []
        for _ in range(certainty_count):
            length = self.vp.get_block_length(self.top_block)
            print(f"Length: {length}")
            if length is None:
                # return True
                is_stacked_count += 1
                continue

            if length > _STACKED_BLOCK_THRESHOLD:
                # return True
                is_stacked_count += 1
                continue
            # else:
                # return False
                # is_stacked_count += 
        is_stacked: bool = float(is_stacked_count) / float(certainty_count) > 0.5
        return is_stacked

