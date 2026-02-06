import numpy as np
from scipy.signal import savgol_filter
import csv

window_size = 11
poly_order = 3

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

x_smoothener = savgol_filter(x, window_size, poly_order)
y_smoothener = savgol_filter(y, window_size, poly_order)
z_smoothener = savgol_filter(z, window_size, poly_order)
rx_smoothener = savgol_filter(rx, window_size, poly_order)
ry_smoothener = savgol_filter(ry, window_size, poly_order)
rz_smoothener = savgol_filter(rz, window_size, poly_order)

clean_data = zip(timestamp, x_smoothener, y_smoothener, z_smoothener, rx_smoothener, ry_smoothener, rz_smoothener, gripper_val)

with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'x', 'y', 'z', 'rx', 'ry', 'rz', 'gripper'])
    writer.writerows(clean_data)
