import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import csv

csv_path = "demo_mycobot.csv"

speed = 30
use_time_stamps = True
fixed_dt = 0.04
max_dt = 0.04
min_dt = 0.04

trajectory_joint_angle = True
trajectory_coords = False

def loading_trajectory_angles(path):
    traj = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = float(row["timestamp"])
            angles = []
            gripper_value = float(row.get("gripper"))
            for i in range(1,7):
                angles.append(float(row[f"j{i}"]))
            traj.append((ts, angles, gripper_value))
    if not traj:
        raise ValueError("CSV is probably empty")
    return traj


def loading_trajectory_coord(path):
    traj = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i % 1 != 0:
                continue

            ts = float(row["timestamp"])

            coordinate = [
                float(row['x']),
                float(row['y']),
                float(row['z']),
                float(row['rx']),
                float(row['ry']),
                float(row['rz'])
            ]

            gripper_pos = float(row['gripper'])

            traj.append((ts, coordinate, gripper_pos))
    if not traj:
        raise ValueError("CSV is probably empty")
    return traj
            


def main():
    mc = MyCobot280(PI_PORT, PI_BAUD)

    if trajectory_coords == True:
        traj = loading_trajectory_coord(csv_path)
        print(f"Loaded {len(traj)} frames from {csv_path}")

        mc.power_on()
        time.sleep(0.5)
        ts0, coordinate0, gripper0 = traj[0]
        print("Going to first recorded pose...")
        mc.send_coords(coordinate0, speed, 1)
        time.sleep(2)
        mc.set_gripper_value(int(gripper0), speed)

        try:
            prev_ts = ts0
            for ts, coords, g in traj:
                # Timing
                if use_time_stamps:
                    dt = ts - prev_ts
                    if dt < 0:
                        dt = fixed_dt
                    dt = max(min_dt, min(max_dt, dt))
                else:
                    dt = fixed_dt

                # Command
                mc.send_coords(coords, speed, 1) # mode = 0
                mc.set_gripper_value(int(g), speed)

                # Wait roughly the recorded interval
                time.sleep(dt)
                prev_ts = ts

        except KeyboardInterrupt:
            print("\nStopped by user (Ctrl+C).")

        print("Done")
    if trajectory_joint_angle == True:
        traj = loading_trajectory_angles(csv_path) 
        print(f"Loaded {len(traj)} frames from {csv_path}")

        mc.power_on()
        time.sleep(0.5)
    
        ts0, angles0, gripper0 = traj[0]
        print("Moving to initial joint configuration")
        mc.send_angles(angles0, speed) 
        time.sleep(3) 
        mc.set_gripper_value(int(gripper0), speed)

        try:
            prev_ts = ts0
            for ts, angles, g in traj:
                # 2. Timing Logic
                if use_time_stamps:
                    dt = ts - prev_ts
                    if dt < 0:
                        dt = fixed_dt
                    dt = max(min_dt, min(max_dt, dt))
                else:
                    dt = fixed_dt

                mc.send_angles(angles, speed) 
                mc.set_gripper_value(int(g), speed)

                time.sleep(dt)
                prev_ts = ts

        except KeyboardInterrupt:
            print("\nPlayback stopped by user.")

        print("Done")


if __name__ == "__main__":
    main()