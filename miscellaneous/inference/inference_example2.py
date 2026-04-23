import json_numpy
import numpy as np
import requests
import time

json_numpy.patch()

SERVER_URL = "http://127.0.0.1:8777/act"
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
    print(f"[{time.strftime('%H:%M:%S')}] Attempting to send {image.nbytes / 1024:.1f} KB to server...", flush=True)

    try:
        resp = requests.post(SERVER_URL, json=payload, timeout=20)
    except Exception as exc:
        print(f"[{time.strftime('%H:%M:%S')}] REQUEST ERROR: {exc}", flush=True)
        return None

    print(f"[{time.strftime('%H:%M:%S')}] Response status: {resp.status_code}", flush=True)

    if resp.status_code == 200:
        return resp.json()

    print(f"[{time.strftime('%H:%M:%S')}] Server Error: {resp.status_code}", flush=True)
    print(resp.text, flush=True)
    return None

def main():
    print("--- OpenVLA Connection Test ---", flush=True)
    end_time = time.time() + 60.0
    attempt = 1

    while time.time() < end_time:
        print(f"\n[{time.strftime('%H:%M:%S')}] Attempt #{attempt}", flush=True)
        try:
            image, state = get_observation()
            raw = send_observation(image, state, INSTRUCTION)
            if raw is not None:
                actions = json_numpy.loads(raw)
                print("✅ SUCCESS! Server returned actions.", flush=True)
                print(f"Action sample: {actions}", flush=True)
            else:
                print("⚠️ No valid response received.", flush=True)
        except Exception as e:
            print(f"❌ FAILED: {e}", flush=True)

        attempt += 1
        time.sleep(1.0)

    print("⏱️ Finished retrying for 60 seconds.", flush=True)

if __name__ == "__main__":
    main()