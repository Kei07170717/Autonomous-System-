import time
import cv2
from dataclasses import dataclass
from typing import Tuple

# Assuming your original code is saved in a file named `vision.py`
from visual_perceptor import VisualPerceptor

@dataclass
class MockBlock:
    """A mock class to simulate the block object your perceptor expects."""
    color: Tuple[int, int, int]
    classification_threshold: int

def main():
    # Example: Looking for a Blue block. 
    # In OpenCV HSV, Blue hue is around 120. 
    # (Adjust this to match the actual physical block you are testing)
    target_block = MockBlock(
        color=(120, 255, 255), 
        classification_threshold=10
    )

    print("Initializing Camera...")
    # Set debug=True to trigger your cv2.imshow windows
    perceptor = VisualPerceptor(mm_per_pixel=0.1, debug=False)
    
    # Give the camera hardware a second to warm up
    time.sleep(1)
    print("Camera ready. Press Ctrl+C in the terminal to stop.")

    try:
        while True:
            pos = perceptor.get_block_pos(target_block)
            
            if pos:
                # The block might disappear in the milliseconds between these calls!
                orientation = perceptor.get_block_orientation(target_block)
                length = perceptor.get_block_length(target_block)
                distance = perceptor.get_block_xy_distance(target_block)

                # Safely format the values, falling back to "N/A" if they returned None
                pos_str = f"{pos[0]:.1f}, {pos[1]:.1f}"
                dist_str = f"X: {distance[0]:.2f}, Y: {distance[1]:.2f}" if distance else "N/A"
                ori_str = f"{orientation:.1f}°" if orientation is not None else "N/A"
                len_str = f"{length:.2f}" if length is not None else "N/A"

                print(f"✅ Block Found!")
                print(f"   Position (px): {pos_str}")
                print(f"   Distance (mm): {dist_str}")
                print(f"   Orientation  : {ori_str}")
                print(f"   Length (mm)  : {len_str}")
                print("-" * 30)
            else:
                print("❌ Block not detected in frame.")
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting debug script...")
    finally:
        perceptor.cleanup()
        print("Cleanup complete.")

if __name__ == "__main__":
    main()
