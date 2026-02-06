import numpy as np
from scipy.signal import savgol_filter
import csv

window_size = 11
poly_order = 4

filename = 'Savitzky_Golay_denoised.csv'

timestamp = []
x = []
y = []
z = []
rx = []
ry = []
rz = []
gripper_val = []


with open('demo_mycobot.csv', 'r') as csv_file:
    reader = csv.DictReader(csv_file)

    for row in reader:
        timestamp.append(row['timestamp'])
        x.append(float(row['x']))
        y.append(float(row['y']))
        z.append(float(row['z']))
        rx.append(float(row['rx']))
        ry.append(float(row['ry']))
        rz.append(float(row['rz']))
        gripper_val.append((row['gripper']))

    csv_file.close()

def smooth_angle_array(angle_list, window, poly):
    rads = np.deg2rad(angle_list)
    unwrapped = np.unwrap(rads)
    smoothed = savgol_filter(unwrapped, window, poly)
    degs = np.rad2deg(smoothed)
    return (degs + 180) % 360 - 180 #back to -180, 180 range


x_smoothener = savgol_filter(x, window_size, poly_order)
y_smoothener = savgol_filter(y, window_size, poly_order)
z_smoothener = savgol_filter(z, window_size, poly_order)
rx_smoothener = smooth_angle_array(rx, window_size, poly_order)
ry_smoothener = smooth_angle_array(ry, window_size, poly_order)
rz_smoothener = smooth_angle_array(rz, window_size, poly_order)

clean_data = zip(timestamp, x_smoothener, y_smoothener, z_smoothener, rx_smoothener, ry_smoothener, rz_smoothener, gripper_val)

with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'x', 'y', 'z', 'rx', 'ry', 'rz', 'gripper'])
    writer.writerows(clean_data)
