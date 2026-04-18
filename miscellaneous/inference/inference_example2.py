import json_numpy
import numpy as np
import requests

json_numpy.patch()

SERVER_URL = "http://cerulean:8777/act"
INSTRUCTION = "pick up the object"

def get_observation():
    image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    state = np.zeros(7, dtype=np.float32)
    return image, state

def send_observation(image, state, instruction):
    payload = {
        "encoded": json_numpy.dumps({
            "full_image": image,
            "state": state,
            "instruction": instruction,
        })
    }
    print(f"Attempting to send {image.nbytes / 1024:.1f} KB to server...")
    resp = requests.post(SERVER_URL, json=payload, timeout=240)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"Server Error: {resp.status_code}")
        print(resp.text)
        return None

def main():
    print("--- OpenVLA Connection Test ---")
    try:
        image, state = get_observation()
        raw = send_observation(image, state, INSTRUCTION)
        if raw is not None:
            actions = json_numpy.loads(raw)
            print("✅ SUCCESS! Server returned actions.")
            print(f"Action sample: {actions[0]}")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    main()