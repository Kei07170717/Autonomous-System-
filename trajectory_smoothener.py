import numpy as np
import csv

def fill_timestamp_gaps(input_csv, output_csv, expected_freq=10, threshold_multiplier=3):
    """
    Fills large timestamp gaps with interpolated waypoints.
    
    Args:
        input_csv: Input CSV file path
        output_csv: Output CSV file path
        expected_freq: Expected recording frequency in Hz (default 10)
        threshold_multiplier: Gaps larger than this * expected_dt get filled
    """
    
    expected_dt = 1.0 / expected_freq
    threshold = expected_dt * threshold_multiplier
    
    print(f"Expected interval: {expected_dt:.3f}s")
    print(f"Gap threshold: {threshold:.3f}s")
    print(f"Filling gaps larger than {threshold:.3f}s with interpolated points\n")
    
    # Load all data
    data = []
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'timestamp': float(row['timestamp']),
                'j1': float(row['j1']),
                'j2': float(row['j2']),
                'j3': float(row['j3']),
                'j4': float(row['j4']),
                'j5': float(row['j5']),
                'j6': float(row['j6']),
                'x': float(row['x']),
                'y': float(row['y']),
                'z': float(row['z']),
                'rx': float(row['rx']),
                'ry': float(row['ry']),
                'rz': float(row['rz']),
                'gripper': float(row['gripper'])
            })
    
    # Fill gaps
    filled_data = []
    for i in range(len(data)):
        filled_data.append(data[i])
        
        if i < len(data) - 1:
            current = data[i]
            next_point = data[i + 1]
            dt = next_point['timestamp'] - current['timestamp']
            
            if dt > threshold:
                # Calculate how many interpolation points needed
                num_fills = int(dt / expected_dt) - 1
                
                print(f"⚠️  Gap detected: {dt:.4f}s between points {i+1} and {i+2}")
                print(f"   Inserting {num_fills} interpolated points")
                
                # Linear interpolation for each field
                for fill_idx in range(1, num_fills + 1):
                    alpha = fill_idx / (num_fills + 1)  # 0 to 1
                    
                    interpolated = {}
                    for key in current.keys():
                        if key == 'gripper':
                            # Keep gripper from previous (step-wise)
                            interpolated[key] = current[key]
                        else:
                            # Linear interpolation
                            interpolated[key] = current[key] + alpha * (next_point[key] - current[key])
                    
                    filled_data.append(interpolated)
    
    # Write output
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'j1', 'j2', 'j3', 'j4', 'j5', 'j6', 
                        'x', 'y', 'z', 'rx', 'ry', 'rz', 'gripper'])
        
        for row in filled_data:
            writer.writerow([
                row['timestamp'], row['j1'], row['j2'], row['j3'], 
                row['j4'], row['j5'], row['j6'], row['x'], row['y'], 
                row['z'], row['rx'], row['ry'], row['rz'], row['gripper']
            ])
    
    print(f"\n✓ Original points: {len(data)}")
    print(f"✓ Filled points: {len(filled_data)}")
    print(f"✓ Added {len(filled_data) - len(data)} interpolated waypoints")
    print(f"✓ Saved to: {output_csv}")


if __name__ == "__main__":
    input_file = input("Enter input CSV filename: ")
    output_file = input("Enter output CSV filename: ")
    freq = float(input("Enter expected frequency (Hz, default 10): ") or "10")
    
    fill_timestamp_gaps(input_file, output_file, expected_freq=freq)