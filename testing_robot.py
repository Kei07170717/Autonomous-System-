import time
from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD  

mc = MyCobot(PI_PORT, PI_BAUD)

print("Starting Robot Test...")

mc.power_on()
time.sleep(1)

print("Moving Home...")
mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(3) # Give it time to mov

print("Moving Joint 2...")
mc.send_angle(2, 40, 50)
time.sleep(2)

<<<<<<< HEAD
mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(3) # Give it time to move
print("Moving joint 3..")
mc.send_angle(1, 160,100)
time.sleep(3)
mc.send_angles([0,0,0, 0,0,0],50)

# 5. Get current state
=======
>>>>>>> 7bdea05 (made changes)
angles = mc.get_angles()
print(f"Current Joint Angles: {angles}")

mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(3) # Give it time to move

print("Test Complete.")