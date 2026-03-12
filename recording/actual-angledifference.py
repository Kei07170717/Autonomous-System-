import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

mc = MyCobot280(PI_PORT, PI_BAUD)
mc.send_angles([50,50,0,0,0,0], 50)
time.sleep(1)
angles1 = mc.get_angles()
time.sleep(1)
mc.send_angles([50,50,50,50,50,50], 50)
time.sleep(1)
angles2 = mc.get_angles()
time.sleep(1)
mc.send_angles([0,0,0,0,0,0], 50)
time.sleep(2)
angles3 = mc.get_angles()
print(angles1)
print(angles2)
print(angles3)

