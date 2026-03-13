import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
mc = MyCobot280(PI_PORT, PI_BAUD)

mc.send_angles([0,0,0,0,0,0], 50)
time.sleep(1)
angles = mc.get_angles()
print(angles)

mc.set_gripper_state(0, 50)
time.sleep(3)  # Open  (speed 0-100)
pos = mc.get_gripper_value()
print(pos)
time.sleep(1)
mc.set_gripper_state(1, 50)  # Close (speed 0-100)
time.sleep(3)
pos1 = mc.get_gripper_value()
print(pos1)
time.sleep(1)
mc.send_angles([0,0,0,0,0,0], 50)
time.sleep(1)
angles1 = mc.get_angles()
print(angles1)




#n = 10
#times = []
#for _ in range(n):
    #mc.send_angles([-50,-50,0,0,0,0], 50)
    #start = time.perf_counter()
    #mc.get_angles()
    #times.append((time.perf_counter()-start)*1000)
    #time.sleep(3)
    #mc.send_angles([0,0,0,0,0,0], 50)
    #time.sleep(3)

#print(f"samples: {n}")
#print(f"mean: {sum(times)/len(times)}ms")
#print(f"min ms difference: {min(times)}ms")
#print(f"max ms difference: {max(times)}ms")


#code to test the angles
#mc.send_angles([-50,-50,0,0,0,0], 50)
#time.sleep(5)
#angles1 = mc.get_angles()
#time.sleep(5)
#ang = mc.get_angles()
#time.sleep(5)
#mc.send_angles([-50,-50,50,0,50,150], 50)
#time.sleep(5)
#angles2 = mc.get_angles()
#time.sleep(5)
#mc.send_angles([-50,-50,50,-50,50,150], 50)
#time.sleep(5)
#angles3 = mc.get_angles()
#time.sleep(5)
#mc.send_angles([0,0,0,0,0,0], 50)
#time.sleep(5)
#angles4 = mc.get_angles()
#print(angles1)
#print(ang)
#print(angles2)
#print(angles3)
#print(angles4)

