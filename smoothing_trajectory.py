import csv
import numpy as np
from scipy.interpolate import interp1d

def smooth_trajectory(input_csv, output_csv, interpolation_factor=5):
    """
    Smooths trajectory by interpolating between waypoints.
    
    Args:
        input_csv: Input CSV file path
        output_csv: Output CSV file path  
        interpolation_factor: How many new points between each original point (higher = smoother)
    """
    
    # Load data
    timestamps = []
    joint_angles = []  # j1-j6
    coords = []  # x, y, z, rx, ry, rz
    gripper_values = []
    
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamps.append(float(row['timestamp']))
            joint_angles.append([
                float(row['j1']),
                float(row['j2']),
                float(row['j3']),
                float(row['j4']),
                float(row['j5']),
                float(row['j6'])
            ])
            coords.append([
                float(row['x']),
                float(row['y']),
                float(row['z']),
                float(row['rx']),
                float(row['ry']),
                float(row['rz'])
            ])
            gripper_values.append(float(row['gripper']))
    
    # Convert to numpy arrays
    timestamps = np.array(timestamps)
    joint_angles = np.array(joint_angles)
    coords = np.array(coords)
    gripper_values = np.array(gripper_values)
    
    # Create normalized parameter (0 to 1)
    original_indices = np.arange(len(timestamps))
    
    # Create interpolated indices
    num_original = len(timestamps)
    num_interpolated = (num_original - 1) * interpolation_factor + 1
    interpolated_indices = np.linspace(0, num_original - 1, num_interpolated)
    
    # Interpolate timestamps
    time_interp = interp1d(original_indices, timestamps, kind='linear')
    new_timestamps = time_interp(interpolated_indices)
    
    # Interpolate joint angles (each joint separately)
    new_joint_angles = np.zeros((num_interpolated, 6))
    for i in range(6):
        joint_interp = interp1d(original_indices, joint_angles[:, i], kind='cubic')
        new_joint_angles[:, i] = joint_interp(interpolated_indices)
    
    # Interpolate coordinates
    new_coords = np.zeros((num_interpolated, 6))
    for i in range(6):
        coord_interp = interp1d(original_indices, coords[:, i], kind='cubic')
        new_coords[:, i] = coord_interp(interpolated_indices)
    
    # Interpolate gripper (step-wise to maintain binary nature)
    gripper_interp = interp1d(original_indices, gripper_values, kind='nearest')
    new_gripper = gripper_interp(interpolated_indices)
    
    # Write smoothed trajectory
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'j1', 'j2', 'j3', 'j4', 'j5', 'j6', 
                        'x', 'y', 'z', 'rx', 'ry', 'rz', 'gripper'])
        
        for i in range(num_interpolated):
            row = [new_timestamps[i]] + \
                  list(new_joint_angles[i]) + \
                  list(new_coords[i]) + \
                  [new_gripper[i]]
            writer.writerow(row)
    
    print(f"Original trajectory: {num_original} points")
    print(f"Smoothed trajectory: {num_interpolated} points")
    print(f"Interpolation factor: {interpolation_factor}x")
    print(f"Saved to: {output_csv}")


if __name__ == "__main__":
    input_file = input("Enter input CSV filename: ")
    output_file = input("Enter output CSV filename: ")
    factor = int(input("Enter interpolation factor (e.g., 5 for 5x more points): "))
    
    smooth_trajectory(input_file, output_file, factor)