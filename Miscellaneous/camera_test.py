import cv2
import time
import os

def snap(cam_index: int, out_path: str, warmup_frames: int = 10):
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {cam_index} (/dev/video{cam_index}).")

    # Optional: set a reasonable capture size (USB cams usually handle this well)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Warm up exposure/auto-focus
    for _ in range(warmup_frames):
        cap.read()
        time.sleep(0.03)

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise RuntimeError("Failed to capture frame.")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    ok = cv2.imwrite(out_path, frame)
    if not ok:
        raise RuntimeError(f"Failed to write image to {out_path}")

    print(f"Saved: {out_path}  shape={frame.shape}")

if __name__ == "__main__":
    cam = int(input("Enter camera number (e.g., 0 or 2): ").strip())
    fn = input("Enter filename to save (e.g., photo.jpg): ").strip()
    snap(cam, fn)
