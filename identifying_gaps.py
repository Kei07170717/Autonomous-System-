import csv

def find_timestamp_gaps(input_csv, expected_freq=10, threshold_multiplier=3):
    """
    Identifies lines with abnormal timestamp gaps in CSV trajectory.
    
    Args:
        input_csv: Path to CSV file
        expected_freq: Expected recording frequency in Hz (default 10)
        threshold_multiplier: How many times expected interval = bad gap (default 3x)
    """
    
    expected_dt = 1.0 / expected_freq  # 0.1s for 10Hz
    threshold = expected_dt * threshold_multiplier  # 0.3s
    
    timestamps = []
    line_numbers = []
    
    print(f"Expected interval: {expected_dt:.3f}s")
    print(f"Gap threshold: {threshold:.3f}s")
    print(f"\n{'='*80}")
    print(f"DETECTED GAPS EXCEEDING {threshold:.3f}s:")
    print(f"{'='*80}\n")
    
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        prev_ts = None
        prev_line = 1  # Header is line 1
        prev_row_data = None
        
        for i, row in enumerate(reader, start=2):  # Data starts at line 2
            current_ts = float(row['timestamp'])
            timestamps.append(current_ts)
            line_numbers.append(i)
            
            if prev_ts is not None:
                dt = current_ts - prev_ts
                
                if dt > threshold:
                    print(f"⚠️  BAD GAP DETECTED:")
                    print(f"   Between CSV lines: {prev_line} → {i}")
                    print(f"   Time gap: {dt:.4f}s ({dt/expected_dt:.1f}x expected)")
                    print(f"   Previous timestamp: {prev_ts:.4f}")
                    print(f"   Current timestamp:  {current_ts:.4f}")
                    print(f"   Previous gripper: {prev_row_data['gripper']}")
                    print(f"   Current gripper:  {row['gripper']}")
                    print(f"\n   Line {prev_line} data: {prev_row_data['timestamp']},{prev_row_data['j1']},{prev_row_data['j2']},{prev_row_data['j3']},{prev_row_data['j4']},{prev_row_data['j5']},{prev_row_data['j6']},gripper={prev_row_data['gripper']}")
                    print(f"   Line {i} data:      {row['timestamp']},{row['j1']},{row['j2']},{row['j3']},{row['j4']},{row['j5']},{row['j6']},gripper={row['gripper']}")
                    print()
            
            prev_ts = current_ts
            prev_line = i
            prev_row_data = row
    
    # Summary statistics
    if len(timestamps) > 1:
        dts = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        avg_dt = sum(dts) / len(dts)
        min_dt = min(dts)
        max_dt = max(dts)
        
        print(f"{'='*80}")
        print("SUMMARY STATISTICS:")
        print(f"{'='*80}")
        print(f"Total frames: {len(timestamps)}")
        print(f"Average interval: {avg_dt:.4f}s ({1/avg_dt:.2f} Hz)")
        print(f"Min interval: {min_dt:.4f}s")
        print(f"Max interval: {max_dt:.4f}s")
        print(f"Expected interval: {expected_dt:.4f}s ({expected_freq} Hz)")


if __name__ == "__main__":
    csv_file = input("Enter CSV filename: ")
    frequency = float(input("Enter expected frequency (Hz, default 10): ") or "10")
    
    find_timestamp_gaps(csv_file, expected_freq=frequency)