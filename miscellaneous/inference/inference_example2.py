"""
Continuous inference client for OpenVLA server.
Sends observations at 10Hz and prints predicted actions.
Requires the server to be running (bash inference.sh).
"""

import json
import time

import json_numpy
import numpy as np
import requests

json_numpy.patch()

SERVER_URL = "http://localhost:8777/act"
INSTRUCTION = "pick up the object"
TARGET_HZ = 10
PERIOD = 1.0 / TARGET_HZ


def get_observation():
    """Get current observation. Replace with real camera + robot state."""
    image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    state = np.zeros(7, dtype=np.float32)
    return image, state


def send_observation(image, state, instruction):
    """Send observation to VLA server and return decoded actions."""
    payload = {
        "encoded": json_numpy.dumps({
            "full_image": image,
            "state": state,
            "instruction": instruction,
        })
    }
    resp = requests.post(SERVER_URL, json=payload)
    raw = resp.json()
    # Decode each json_numpy-encoded action array
    actions = [json_numpy.loads(json.dumps(a)) for a in raw]
    return actions


def main():
    print(f"Starting inference loop at {TARGET_HZ}Hz")
    print(f"Instruction: '{INSTRUCTION}'")
    print(f"Server: {SERVER_URL}")
    print("Press Ctrl+C to stop\n")

    step = 0
    while True:
        t_start = time.time()

        image, state = get_observation()
        actions = send_observation(image, state, INSTRUCTION)

        # Print first action from the chunk (the immediate next action)
        print(f"[Step {step:04d}] Action 0: {actions[0]}")

        step += 1

        # Sleep to maintain target frequency
        elapsed = time.time() - t_start
        sleep_time = PERIOD - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            actual_hz = 1.0 / elapsed if elapsed > 0 else float("inf")
            print(f"  Warning: inference took {elapsed:.3f}s ({actual_hz:.1f}Hz < {TARGET_HZ}Hz)")


if __name__ == "__main__":
    main()