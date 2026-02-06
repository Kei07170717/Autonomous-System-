import time
from pymycobot import MyCobot280, PI_PORT, PI_BAUD

mc = MyCobot280(PI_PORT, PI_BAUD)

print("power:", mc.is_power_on())
print("paused:", mc.is_paused())
print("moving:", mc.is_moving())
print("coords:", mc.get_coords())
print("angles:", mc.get_angles())
mc.send_angles([0, 0, 0, 0, 0, 0], 50)
# Try to unstick common states:
mc.power_on()
mc.resume()               # unpause ALL if paused
time.sleep(0.5)

print("\nSending coords...")
mc.send_coords([120, 0, 120, 0, 0, 0], 30, 0)

# Watch for change for 5 seconds:
for i in range(10):
    print(i, "moving:", mc.is_moving(), "coords:", mc.get_coords())
    time.sleep(0.5)