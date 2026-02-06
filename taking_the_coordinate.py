import time
from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD 
import csv 

mc = MyCobot(PI_PORT, PI_BAUD)

print("Starting")

data_buffer = []
recording = True

mc.power_on()
time.sleep(1)

print("Setting it to initial position")
mc.send_angles([0, 0, 0, 0, 0, 0], 50)
time.sleep(5) # Give it time to mov

mc.release_all_servos
time.sleep(1)

while not mc.is_btn_clicked(1):

    timestamp = time.time()
    angles = mc.get_angles() #Get angles and time

    if angles and len(angles) == 6:
        data_buffer.append([timestamp] + angles)

    time.sleep(0.1) #10 Hz

mc.power_on()
time.sleep(1)
mc.send_angles([0, 0, 0, 0, 0, 0], 50) #return it home

filename = f"demo_mycobot.csv"
with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'j1', 'j2', 'j3', 'j4', 'j5', 'j6'])
    writer.writerows(data_buffer)

print(f"Data saved to {filename}")

print("Test Complete.")