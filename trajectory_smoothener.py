import numpy as np
from scipy.signal import savgol_filter
import csv

window_size = 11
poly_order = 4

filename = input("Please select the filename to write to:")

timestamp = []
j1 = []
j2 = []
j3 = []
j4 = []
j5 = []
j6 = []

x = []
y = []
z = []
rx = []
ry = []
rz = []
gripper_val = []

trajectory_joint_angle = True
trajectory_coords = False

def smooth_angle_array(angle_list, window, poly):
        rads = np.deg2rad(angle_list)
        unwrapped = np.unwrap(rads)
        smoothed = savgol_filter(unwrapped, window, poly)
        degs = np.rad2deg(smoothed)
        return (degs + 180) % 360 - 180 #back to -180, 180 range

if trajectory_coords == True:
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
    rx_smoothener = smooth_angle_array(rx, window_size, poly_order)
    ry_smoothener = smooth_angle_array(ry, window_size, poly_order)
    rz_smoothener = smooth_angle_array(rz, window_size, poly_order)

    clean_data = zip(timestamp, x_smoothener, y_smoothener, z_smoothener, rx_smoothener, ry_smoothener, rz_smoothener, gripper_val)
    header = ['timestamp', 'x', 'y', 'z', 'rx', 'ry', 'rz', 'gripper']

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(clean_data)

if trajectory_joint_angle == True:
    with open('demo_mycobot.csv', 'r') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            timestamp.append(row['timestamp'])
            j1.append(float(row['j1']))
            j2.append(float(row['j2']))
            j3.append(float(row['j3']))
            j4.append(float(row['j4']))
            j5.append(float(row['j5']))
            j6.append(float(row['j6']))
            gripper_val.append((row['gripper']))

        csv_file.close()

    
    j1_smoothener = savgol_filter(j1, window_size, poly_order)
    j2_smoothener = savgol_filter(j2, window_size, poly_order)
    j3_smoothener = savgol_filter(j3, window_size, poly_order)
    j4_smoothener = savgol_filter(j4, window_size, poly_order)
    j5_smoothener = savgol_filter(j5, window_size, poly_order)
    j6_smoothener = savgol_filter(j6, window_size, poly_order)

    clean_data = zip(timestamp, j1, j2, j3, j4, j5, j6, gripper_val)
    header = ['timestamp', 'j1', 'j2', 'j3', 'j4', 'j5', 'j6', 'gripper']

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(clean_data)

