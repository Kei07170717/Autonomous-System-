

from cobot import Cobot
from controller import StackController
from visual_perceptor import VisualPerceptor

def main():
    print('Starting...')
    cobot: Cobot = Cobot()
    visual_perceptor: VisualPerceptor = VisualPerceptor(mm_per_pixel=0.09, debug=False)
    controller: StackController = StackController(cobot, visual_perceptor) 

    controller.start()

if __name__ == '__main__':
    main()
