

from cobot import Cobot
from controller import StackController
from visual_perceptor import VisualPerceptor

def main():
    print('Starting...')
    cobot: Cobot = Cobot()
    visual_perceptor: VisualPerceptor = VisualPerceptor()
    controller: StackController = StackController(cobot, visual_perceptor) 

if __name__ == '__main__':
    main()
