import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
mc = MyCobot280(PI_PORT, PI_BAUD)

n = 50
times = []
for _ in range(n):
    start = time.perf_counter()
    angles = mc.get_angles()
    times.append(time.perf_counter - start)

times_ms = [t*1000 for t in times]
print(f"Samples:  {n}")
print(f"Mean:     {sum(times_ms)/len(times_ms):.2f}ms")
print(f"Min:      {min(times_ms):.2f}ms")
print(f"Max:      {max(times_ms):.2f}ms")




#code to test the angles
#mc.send_angles([-50,-50,0,0,0,0], 50)
#time.sleep(5)
#angles1 = mc.get_angles()
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
#print(angles2)
#print(angles3)
#print(angles4)

