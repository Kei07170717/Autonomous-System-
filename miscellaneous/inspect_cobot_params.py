import time
from pymycobot import *

# Define your serial port. Change 'COM30' if your arm is on a different port.
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

# Connect to the robotic arm
try:
    mc = MyCobot280(PI_PORT, str(PI_BAUD))

    print("Successfully connected to the robotic arm.\n")
except Exception as e:
    print(f"Error: {e}")
    print("Could not connect. Please check if the port is correct and not in use by another program.")
    exit()

# ---------------------------------------------------------
# 1. OVERALL SYSTEM & MOVEMENT STATUS
# ---------------------------------------------------------
print("=== System & Movement Status ===")

# Fresh Mode (0: Interpolation, 1: Refresh)
try:
    fresh_mode = mc.get_fresh_mode()
    mode_name = "Refresh Mode" if fresh_mode == 1 else "Interpolation Mode" if fresh_mode == 0 else f"Unknown ({fresh_mode})"
    print(f"Fresh Mode      : {mode_name}")
except Exception:
    print("Fresh Mode      : Unsupported or Error")

# Sports Mode / Movement Type (1: movel, 0: moveJ)
try:
    move_type = mc.get_movement_type()
    move_name = "Linear (movel)" if move_type == 1 else "Joint (moveJ)" if move_type == 0 else f"Unknown ({move_type})"
    print(f"Sports Mode     : {move_name}")
except Exception:
    print("Sports Mode     : Unsupported or Error")

# Free Mode (1: Free mode open, 0: Free mode closed)
try:
    free_mode = mc.is_free_mode()
    free_name = "Enabled (Limp/Draggable)" if free_mode == 1 else "Disabled (Holding Torque)"
    print(f"Free Mode       : {free_name}")
except Exception:
    print("Free Mode       : Unsupported or Error")

# Error Information (0: No error)
try:
    err = mc.get_error_information()
    err_name = "No Errors" if err == 0 else f"Error Code {err}"
    print(f"Robot Errors    : {err_name}")
except Exception:
    pass

print("\n" + "="*40)
print("=== Servo PID & Mode Information ===")
print("="*40)

# ---------------------------------------------------------
# 2. SERVO PID & MODE LOOP
# ---------------------------------------------------------
# Common memory addresses for P, I, D in standard robotic servos. 
# (Change these to 26, 27, 28 if your specific servo model requires it).
ADDR_P = 21 
ADDR_I = 22
ADDR_D = 24 

# Loop through joints 1 through 6
for i in range(1, 7):
    # Read the custom mode data at address 23 (from your original script)
    current_value = mc.get_servo_data(i, 23)
    time.sleep(0.05) # Tiny pause between serial calls
    
    # Translate the mode number into plain English
    if current_value == 0:
        mode = "Smooth/Stable Mode"
    elif current_value == 4:
        mode = "High-Precision Mode"
    else:
        mode = f"Unknown Mode (Value: {current_value})"
        
    # Read actual P, I, D gains
    p_val = mc.get_servo_data(i, ADDR_P)
    time.sleep(0.05)
    
    i_val = mc.get_servo_data(i, ADDR_I)
    time.sleep(0.05)
    
    d_val = mc.get_servo_data(i, ADDR_D)
    
    # Print the compiled data for the joint
    print(f"[ Joint {i} ] : {mode}")
    print(f"   -> P (Proportional) Gain : {p_val}")
    print(f"   -> I (Integral) Gain     : {i_val}")
    print(f"   -> D (Derivative) Gain   : {d_val}")
    print("-" * 40)
    
    # Pause before querying the next joint to prevent bus overload
    time.sleep(0.1) 

print("Data reading complete.")
