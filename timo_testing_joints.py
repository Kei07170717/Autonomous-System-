import time
from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD  # These are pre-set for the 280 Pi
 # 1. Initialize the robot
# On the 280 Pi, the port is usually "/dev/ttyAMA0" and baud is 1000000
mc = MyCobot(PI_PORT, PI_BAUD)
def init(mc):
    """This function will activate/ initialize the robot this must be run before the start of the """
    print("Starting Robot Test...")
    # 2. Wake up the motors
    mc.power_on()
    time.sleep(1)
    return mc
#initializing the start
start=init(mc) # This var stores the My cobolt info as well as 

# 3. Move to Home position (All 6 joints at 0 degrees)
# Parameters: [J1, J2, J3, J4, J5, J6], speed (1-100)
print("Moving to Home...")
mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(3) # Give it time to move

def lower_joints():
    # 4. Simple movement: Move Joint 2 to 40 degrees
    print("moving joint 1 ")
    mc.send_angle(1,150,50)
    time.sleep(1)
    print("Moving Joint 2...")
    mc.send_angle(2, -90, 50)
    print("moving joint 3")
    mc.send_angle(4,90,50)
    time.sleep(2)
    mc.send_angle(4, -55, 40)
    time.sleep(2)
    mc.send_angle(4,30,40)
    time.sleep(2)
    mc.send_angle(4,-55,100)
    time.sleep(2)
    mc.send_angle(4,30,100)
    time.sleep(2)
    print("Getting angle currently", mc.get_angles())
   #print("Moving joint 1 168 -> maximum it can turn")
    #mc.send_angle(1,168,50)
    time.sleep(1)
    mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    return True

def upper_joints():
    print("Moving joint 5")
    mc.send_angle(5,50, 50)
    time.sleep(3)
    print("Moving joint 6")
    mc.send_angle(6,-50,50)
    time.sleep(2)
    mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    return True
   

#run_lower=lower_joints()
mc.send_angle(1,168,50)
time.sleep(5)
mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(5)
mc.send_angle(1,-168,50)
time.sleep(5)

#run_upper=upper_joints()

#mc.send_coords([120, 0, 120, 0, 0, 0], 30, 0)
# 5. Get current state
angles = mc.get_angles()
print(f"Current Joint Angles: {angles}")
#spicy stuff

print("Test Complete.")
mc.send_angles([0, 0, 0, 0, 0, 0], 50)