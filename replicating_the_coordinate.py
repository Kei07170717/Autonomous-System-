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

def main():
    mc = MyCobot280(PI_PORT, PI_BAUD)

    traj = loading_trajectory(csv_path)
    print(f"Loaded {len(traj)} frames from {csv_path}")

    # Optional: go to first frame before replay
    mc.power_on()
    time.sleep(0.5)
    first_angles = traj[0][1]
    print("Going to first recorded pose...")
    mc.send_angles(first_angles, speed)
    time.sleep(2)

    try:
        prev_ts = traj[0][0]
        for ts, angles in traj:
            # Timing
            if use_time_stamps:
                dt = ts - prev_ts
                if dt < 0:
                    dt = fixed_dt
                dt = max(min_dt, min(max_dt, dt))
            else:
                dt = fixed_dt

            # Command
            mc.send_angles(angles, speed)

            # Wait roughly the recorded interval
            time.sleep(dt)
            prev_ts = ts

    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C).")


    print("Done")


if __name__ == "__main__":
    main()