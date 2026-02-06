import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import csv

mc = MyCobot280(PI_PORT, PI_BAUD)

print("Starting")

data_buffer = []

mc.power_on()
time.sleep(1)

print("Setting it to initial position")
mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(5)

mc.release_all_servos() 
time.sleep(1)

Bin_pin = 39
mc.set_pin_mode(Bin_pin, 2)
time.sleep(1)

print("Recording, press head button to stop")

# Button not pressed = 1
while True:
    try:
        btn = mc.get_digital_input(Bin_pin)
    except Exception:
        time.sleep(0.05)
        continue

    if btn == 0:
        break

    timestamp = time.time()
    angles = mc.get_angles()
    print(angles)

    if angles and len(angles) == 6:
        data_buffer.append([timestamp] + angles)

    time.sleep(0.1)

print("Button pressed, stopping recording")

mc.power_on()
time.sleep(1)
mc.send_angles([0, 0, 0, 0, 0, 0], 50)

filename = "demo_mycobot.csv"
with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'j1', 'j2', 'j3', 'j4', 'j5', 'j6'])
    writer.writerows(data_buffer)

print(f"Data saved to {filename}")
print("Test Complete.")
