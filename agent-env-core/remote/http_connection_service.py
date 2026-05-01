import requests
from remote.interfaces import IRemoteActionProvider
import json_numpy
import numpy as np
import time

# 1. Patch the standard json module to handle NumPy arrays
json_numpy.patch()


class HTTPRemoteActionProvider(IRemoteActionProvider):
    def __init__(self, server_url: str, debug: bool = True):
        self.server_url: str = server_url
        self.debug: bool = debug

    def fetch_actions(self, obs: dict) -> list[dict]:
        payload = self._map_obs_to_payload(obs)

        try:
            if self.debug:
                start_time = time.perf_counter()

            response = requests.post(self.server_url, json=payload, timeout=10)

            if self.debug:
                elapsed_time = time.perf_counter() - start_time
                print(
                    f"API request took {elapsed_time:.4f} seconds."
                )
            response.raise_for_status()
            actions = self._map_response_to_actions(response.json())

            assert len(actions) != 0, "Response actions are not expected to be empty"
            return actions

        except requests.exceptions.RequestException as e:
            print(f"Failed to connect or fetch data: {e}")

        return []

    def _map_obs_to_payload(self, obs: dict) -> dict:
        assert obs["instruction"] is not None

        payload = {
            "encoded": json_numpy.dumps(
                {
                    "full_image": obs["cam_external"],
                    "wrist_image": obs["cam_wrist"],
                    "state": np.hstack((obs["arm_angles"], [0], [1.0 - (obs["gripper"] / 100.0)])),
                    "instruction": obs["instruction"],
                }
            )
        }

        return payload

    def _map_response_to_actions(self, raw_data) -> list[dict]:
        raw_actions = json_numpy.loads(raw_data)

        actions = []
        for row in raw_actions:
            actions.append(
                {
                    "arm_angles": row[:6].astype(np.float32),
                    "gripper": np.array(row[7], dtype=np.uint8),
                }
            )

        return actions

    def is_alive(self) -> bool:
        try:
            requests.head(self.server_url, timeout=2)
            return True
        except requests.RequestException:
            return False
