import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import csv

csv_path = "demo_mycobot.csv"

speed = 40
use_time_stamps = True
fixed_dt = 0.10
max_dt = 0.30
min_dt = 0.02


def loading_trajectory(path):
    traj = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = float(row["timestamp"])
            angles = []
            for i in range(1,7):
                angles.append(float(row[f"j{i}"]))
            traj.append((ts, angles))
    if not traj:
        raise ValueError("CSV is probably empty")
    return traj


def loading_trajectory_coord(path):
    traj = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for i in range(0, len(reader), 5):
            ts = float(reader[i]["timestamp"])
            coordinate = []
            coordinate.append(float(reader[i]['x']))
            coordinate.append(float(reader[i]['y']))
            coordinate.append(float(reader[i]['z']))
            coordinate.append(float(reader[i]['rx']))
            coordinate.append(float(reader[i]['ry']))
            coordinate.append(float(reader[i]['rz']))
            gripper_pos = float(reader[i]['gripper'])
            traj.append((ts, coordinate, gripper_pos))
    if not traj:
        raise ValueError("CSV is probably empty")
    return traj
            


def main():
    mc = MyCobot280(PI_PORT, PI_BAUD)

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


if __name__ == "__main__":
    main()