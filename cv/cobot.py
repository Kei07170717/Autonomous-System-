from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

class Cobot():

    def __init__(self) -> None:
        self.mc = MyCobot280(PI_PORT, str(PI_BAUD))
