import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import math

freq = int(input("Please type your selected frequency"))
T = 1/freq

gripper_interval = int(input("Please select gripper movement interval"))
# Every 15 steps lets say

speed = int(input("Please select the speed of the robot movement"))

time_of_run = int(input("Please select how long you want to run the robot for (seconds)"))
time_step_needed = int(time_of_run * freq)

amplitude = 20

def move_generator(t, amp):
    j1 = amp * math.sin(t)
    j2 = amp * math.sin(t + 1)
    j3 = amp * math.sin(t + 2)
    j4 = amp * math.sin(t + 3)
    j5 = amp * math.sin(t + 4)
    j6 = amp * math.sin(t + 5)
    return [j1, j2, j3, j4, j5, j6]

def load_trajectory(total_steps, amp, g_interval):
    buffer = []
    for s in range(total_steps):
        t = s * T
        angles = move_generator(t, amp)
        
        # Calculate gripper state (True for closed/100, False for open/0)
    
        gripper_state = 95 if (s // g_interval) % 2 == 0 else 0
        
        buffer.append([angles, gripper_state])
    return buffer
    



def main():
    trajectory_buffer = load_trajectory(time_step_needed, amplitude, gripper_interval)

    mc = MyCobot280(PI_PORT, PI_BAUD)

    mc.power_on()
    time.sleep(1)

    #initial position
    mc.send_angles([0,0,0,0,0,0], speed)
    time.sleep(2)
    mc.set_gripper_value(0, speed) #speed = 30
    last_g_val = 0
    
    start_time = time.time()

    try:
        for i in range(len(trajectory_buffer)):
            # Precise timing sync
            next_step_time = start_time + (i * T)
            
            # Pull data from buffer
            data = trajectory_buffer[i]
            current_angles = data[0]
            current_g_val = data[1]

            # Execute Arm Movement
            mc.send_angles(current_angles, speed)

            # Execute Gripper ONLY on state change (The Jitter Fix)
            if current_g_val != last_g_val:
                time.sleep(0.02) # Serial Breather
                mc.set_gripper_value(current_g_val, speed)
                last_g_val = current_g_val
                time.sleep(0.02) # Post-gripper Breather

            # Wait until exactly the right time for the next frame
            wait = next_step_time - time.time()
            if wait > 0:
                time.sleep(wait)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        mc.stop()
        mc.release_all_servos()
        print("Done.")

if __name__ == "__main__":
    main()







