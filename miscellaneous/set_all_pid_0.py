import time
from pymycobot.mycobot280 import MyCobot280

from pymycobot import PI_PORT, PI_BAUD
# Define your serial port. Change 'COM30' if your arm is on a different port.

# Connect to the robotic arm
try:
    mc = MyCobot280(PI_PORT, str(PI_BAUD))
    print("Successfully connected to the robotic arm.\n")
except Exception as e:
    print(e)
    print("Error: Could not connect. Please check if the port is correct and not in use by another program.")
    exit()


#joint_id = 1 - 6.
for i in range(1,6):
    mc.set_servo_data(i,23,0)
    time.sleep(1)
    print(mc.get_servo_data(i,23))
