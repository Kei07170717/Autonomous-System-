

from cobot import Cobot
from controller import Controller
from visual_perceptor import VisualPerceptor

def main():
    print('Starting...')
    cobot: Cobot = Cobot()
    visual_perceptor: VisualPerceptor = VisualPerceptor()
    controller: Controller = Controller(cobot, visual_perceptor) 

if __name__ == '__main__':
    main()
