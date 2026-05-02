
from cobot import Cobot
from visual_perceptor import VisualPerceptor


class Controller():
    
    def __init__(self, cobot: Cobot, visual_perceptor: VisualPerceptor) -> None:
        self.cobot = cobot
        self.vp = visual_perceptor
