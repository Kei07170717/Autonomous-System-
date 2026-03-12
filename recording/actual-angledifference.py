import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

mc = MyCobot280(PI_PORT, PI_BAUD)
mc.send_angles([0,0,0,0,0,0], 50)
angles = mc.get_angles()
print(angles)

