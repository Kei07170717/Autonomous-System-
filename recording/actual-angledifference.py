import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

mc = MyCobot280(PI_PORT, PI_BAUD)
mc.send_angles([50,0,0,0,0,0], 50)
time.sleep(1)
angless = mc.get_angles()
mc.send_angles([50,50,50,50,50,50], 50)
time.sleep(1)
mc.send_angles([0,0,0,0,0,0], 50)
time.sleep(2)
angles = mc.get_angles()
print(angless)
print(angles)

