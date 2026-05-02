
from block import Block
from cobot import Cobot
from visual_perceptor import VisualPerceptor
import time

class StackController():
    
    def __init__(self, cobot: Cobot, visual_perceptor: VisualPerceptor) -> None:
        self.cobot = cobot
        self.vp = visual_perceptor
        blue_block = Block(color=(120, 255, 255), classification_threshold=15.0)
        red_block = Block(color=(0, 255, 255), classification_threshold=10.0)
        self.top_block: Block = red_block
        self.bottom_block: Block = blue_block

    def start(self):
        strat = self._locate_top_block
        while strat != None:
            strat = strat()

    def _locate_top_block(self):
        self.cobot.open_gripper()
        while self.vp.get_block_pos(self.top_block) is None:
            self._explore_space()

        self.cobot.stop_moving()
        while True:
            time.sleep(0.5)
            print(f"Block pos: {self.vp.get_block_xy_distance(self.top_block)}")


    def _grab_top_block(self):
        return None
    
    def _locate_bottom_block(self):
        return None

    def _stack_top_block(self):
        return None

    def _explore_space(self):
        pass
