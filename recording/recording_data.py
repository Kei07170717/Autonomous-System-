import cv2
import time 
import os
import numpy as np
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import csv
from replicating_the_coordinate import loading_trajectory_angles, create_chunks

"""
READ THIS BEFORE USE❗️
This python file is for creating recording of the files for 
robotics. 

Each sample file should contain the following:
- joints.npy
- wrist_cam.mp4
- external_cam.mp4

Practice:
Please use the following: 
- When asked for sample number, just provide the number.

The output of the file should look as following (for ex. Sample 1):
- sample_1.npy
- wrist_cam_1.mp4
- external_cam_1.mp4
"""


def replay_trajectory_with_recording(
        csv_path, 
        wrist_cam_writer, 
        external_cam_writer, 
        wrist_cam, 
        external_cam,
        speed,
        T,
        gripper_interval):
    
    mc = MyCobot280(PI_PORT, PI_BAUD)

    #Logs
    joint_angles_state_rec = [] #Joint angles we are sending
    joint_angles_action_rec = [] #actual joint angles output from the robot
    grip_desired = [] #state of grip desired (but won't send every timestamp due to jittery)
    grip_applied = [] #state of grip actually applied
    time_stamp = []


    #Loading the replay trajectory from csv file
    traj = loading_trajectory_angles(csv_path) 
    if not traj:
        raise ValueError("Trajectory not here")
    print(f"Loaded {len(traj)} frames from {csv_path}")

    #Setting the chunk size for the replay
    chunk_size = 10
    chunks = create_chunks(traj, chunk_size)

    #Turn the robot on
    mc.power_on()
    time.sleep(0.5)

    #Loading chunks, setting up the initial position
    ts0, angles0, gripper0 = traj[0]
    print("Moving to initial joint configuration...")
    mc.send_angles(angles0, speed) 
    time.sleep(5) 
    mc.set_gripper_value(int(gripper0), speed)
    time.sleep(2)

    last_gripper_val = int(gripper0)
    gripper_steps_counter = gripper_interval + 1 

    print("Starting chunked playback...")
    start_time = time.monotonic()
    step_count = 0

    try:
        for chunk_idx, chunk in enumerate(chunks):
            print(f"Processing chunk {chunk_idx + 1}/{len(chunks)}")

            for ts, angles, gripper_val in chunk:
                # Calculate precise timing
                next_step_time = start_time + (step_count * T)
                wait0 = next_step_time - time.monotonic() 
                if wait0 > 0:
                    time.sleep(wait0)

                current_time = time.monotonic() - start_time
                time_stamp.append(current_time)

                ret_wrist, frame_wrist = wrist_cam.read()
                if ret_wrist:
                    wrist_cam_writer.write(frame_wrist)

                ret_external, frame_external = external_cam.read()
                if ret_external:
                    external_cam_writer.write(frame_external)

            
                joint_angles_state_rec.append(mc.get_angles()) #mesured state

                joint_angles_action_rec.append(angles) #commanded action
                
                # Send joint angles
                mc.send_angles(angles, speed)

                time.sleep(0.01)

                g_val = int(gripper_val)
                grip_desired.append(g_val)
                
                applied_gripper_val = last_gripper_val
                if gripper_val != last_gripper_val:
                    if gripper_steps_counter >= gripper_interval:
                        time.sleep(0.02) 
                        mc.set_gripper_value(int(gripper_val), speed)
                        time.sleep(0.02)  
                        
                        last_gripper_val = gripper_val
                        gripper_steps_counter = 0 
                        applied_gripper_val = gripper_val
                    
                grip_applied.append(applied_gripper_val) #Record the gripper of actually applied gripper value
                gripper_steps_counter += 1
                
                step_count += 1

    except KeyboardInterrupt:
        print("\nPlayback stopped by the user.")

    
    print("Done")
    return joint_angles_state_rec, joint_angles_action_rec, grip_desired, grip_applied, time_stamp

def resize_video_to_square(in_path, out_path, out_size=(240, 240), fps=10):
    cap = cv2.VideoCapture(in_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open input video: {in_path}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, out_size)
    if not writer.isOpened():
        cap.release()
        raise RuntimeError(f"Could not open output video writer: {out_path}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Resizeto 240x240 
        frame_resized = cv2.resize(frame, out_size, interpolation=cv2.INTER_AREA)
        writer.write(frame_resized)

    cap.release()
    writer.release()


def saving_file(npy_file_name, 
                s, 
                a, 
                gripper_state, 
                gripper_action, 
                time_stamp, 
                wrist_video_path,
                external_video_path,
                control_hz,
                instruction):
    
    state_array = np.array(s, dtype = np.float32) #float val
    action_array = np.array(a, dtype = np.float32)
    gripper_state_array = np.array(gripper_state, dtype = np.int8) #int val
    gripper_action_array = np.array(gripper_action, dtype = np.int8)
    ts_array = np.array(time_stamp, dtype = np.float64)


    info_dict = {
                "Timestamp": ts_array, 
                "Arm_state": state_array,
                 "Arm_action": action_array,
                 "Gripper_desired_state": gripper_state_array,
                 "Gripper_actual_state": gripper_action_array,
                 "wrist_video": os.path.basename(wrist_video_path),
                 "external_video": os.path.basename(external_video_path),
                 "control_hz": float(control_hz), 
                 "instruction": instruction
                 }

    
    np.save(npy_file_name, info_dict, allow_pickle=True)

def main():
    # User input
    sample_num = input("Please type the sample number: ")
    csv_path = input("Please select the csv file to use: ")

    speed = int(input("Please choose the speed: "))
    freq = float(input("Please type frequency: "))
    T = 1/freq

    instruction = input("Prompt for the instruction: ").strip()

    #Dataset folder and filenames
    sample_dir = f"sample_{sample_num}" #directory for the sample
    os.makedirs(sample_dir, exist_ok=True)

    npy_file_name = os.path.join(sample_dir, f"sample_{sample_num}.npy")
    wrist_cam_name = os.path.join(sample_dir, f"wrist_cam_{sample_num}.mp4")
    external_cam_name = os.path.join(sample_dir, f"external_cam_{sample_num}.mp4")

    #Camera configuration
    target_w = 640
    target_h = 480
    fps = int(round(freq))


    wrist_cam = cv2.VideoCapture(0)
    external_cam = cv2.VideoCapture(2)

    wrist_cam.set(cv2.CAP_PROP_FRAME_WIDTH, target_w)
    wrist_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, target_h)
    wrist_cam.set(cv2.CAP_PROP_FPS, fps)
    external_cam.set(cv2.CAP_PROP_FRAME_WIDTH, target_w)
    external_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, target_h)
    external_cam.set(cv2.CAP_PROP_FPS, fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    wrist_writer = cv2.VideoWriter(wrist_cam_name, fourcc, fps, (target_w,target_h))
    ext_writer = cv2.VideoWriter(external_cam_name, fourcc, fps, (target_w,target_h))


    gripper_interval = 25

    try:
        s, a, g_s, g_a, ts = replay_trajectory_with_recording(
            csv_path, 
            wrist_writer, 
            ext_writer, 
            wrist_cam, 
            external_cam,
            speed,
            T,
            gripper_interval)
        
    except Exception as e:
        print(f"Recording has failed: {e}")
        return

    finally: #Forcing release
        wrist_cam.release()
        external_cam.release()
        wrist_writer.release()
        ext_writer.release()

    wrist_cam_240 = wrist_cam_name.replace(".mp4", "_240.mp4")
    external_cam_240 = external_cam_name.replace(".mp4", "_240.mp4")

    resize_video_to_square(wrist_cam_name, wrist_cam_240, out_size=(240, 240))
    resize_video_to_square(external_cam_name, external_cam_240, out_size=(240, 240))


    saving_file(npy_file_name,
                s, 
                a, 
                g_s, 
                g_a, 
                ts,
                wrist_video_path= wrist_cam_240,
                external_video_path=external_cam_240, 
                control_hz = freq,
                instruction = instruction)
    
    print(f"Saved sample to folder: {sample_dir}")
    print(f"- {os.path.basename(npy_file_name)}")
    print(f"- {os.path.basename(wrist_cam_name)}")
    print(f"- {os.path.basename(external_cam_name)}")


if __name__ == "__main__":
    main()
