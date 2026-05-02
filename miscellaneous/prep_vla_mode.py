import time
from pymycobot.mycobot280 import MyCobot280

from pymycobot import PI_PORT, PI_BAUD
# Define your serial port. Change 'COM30' if your arm is on a different port.

# Connect to the robotic arm
mc = MyCobot280(PI_PORT, str(PI_BAUD))


#joint_id = 1 - 6.
for i in range(1,6):
    mc.set_servo_data(i,23,4)
    time.sleep(1)
    print(mc.get_servo_data(i,23))

mc.set_fresh_mode(1)
print("Set fresh mode:", mc.get_fresh_mode())
