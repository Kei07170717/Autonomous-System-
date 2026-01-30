import time
from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD  # These are pre-set for the 280 Pi

# 1. Initialize the robot
# On the 280 Pi, the port is usually "/dev/ttyAMA0" and baud is 1000000
mc = MyCobot(PI_PORT, PI_BAUD)

print("Starting Robot Test...")

# 2. Wake up the motors
mc.power_on()
time.sleep(1)

# 3. Move to Home position (All 6 joints at 0 degrees)
# Parameters: [J1, J2, J3, J4, J5, J6], speed (1-100)
print("Moving to Home...")
mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(3) # Give it time to move

# 4. Simple movement: Move Joint 2 to 40 degrees
print("Moving Joint 2...")
mc.send_angle(2, 40, 50)
time.sleep(2)

# 5. Get current state
angles = mc.get_angles()
print(f"Current Joint Angles: {angles}")

mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(3) # Give it time to move

print("Test Complete.")