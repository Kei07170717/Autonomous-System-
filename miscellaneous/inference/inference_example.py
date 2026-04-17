import h5py
import numpy as np
import cv2
from pathlib import Path
import os

def load_sample(h5_path, t=0):
    with h5py.File(h5_path, "r") as f:
        obs = f["observations"]
        act = f["actions"]

        sample = {
            "arm_angles": obs["arm_angles"][t].astype(np.float32),
            "gripper": np.uint8(obs["gripper"][t]),
            "cam_external": obs["cam_external"][t],
            "cam_wrist": obs["cam_wrist"][t],
            "language_instruction": f.attrs["task"],
        }

        # Resize if needed (match training: 224x224)
        def resize(img):
            if img.shape[:2] != (224, 224):
                return cv2.resize(img, (224, 224))
            return img

        sample["cam_external"] = resize(sample["cam_external"])
        sample["cam_wrist"] = resize(sample["cam_wrist"])

        return sample


def to_model_input(sample):
    return {
        "image": sample["cam_external"],   # or wrist depending on config
        "wrist_image": sample["cam_wrist"],
        "proprio": np.concatenate([
            sample["arm_angles"],
            np.array([sample["gripper"]], dtype=np.float32)
        ]),
        "instruction": sample["language_instruction"],
    }


def find_first_h5(base_dir="."):
    base_path = Path(base_dir)

    # if not base_path.exists():
    #     os.mkdir("_insert_sample_h5_here")

    h5_files = sorted(
        p for p in base_path.rglob("*")
        if p.is_file() and p.suffix in {".h5", ".hdf5"}
    )

    if not h5_files:
        raise FileNotFoundError(f"No .h5/.hdf5 files found in {base_path}")

    return h5_files[0]


"""ADD MODEL AND LORA HERE"""
# model = 

h5_path = find_first_h5()
sample = load_sample(h5_path, t=10)
model_input = to_model_input(sample)
# action = model.step(**model_input)
# print(action)
