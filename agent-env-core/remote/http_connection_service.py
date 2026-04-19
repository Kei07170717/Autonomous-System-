import requests
from remote.interfaces import IRemoteActionProvider
import json_numpy
import numpy as np

# 1. Patch the standard json module to handle NumPy arrays
json_numpy.patch()


class HTTPRemoteActionProvider(IRemoteActionProvider):
    def __init__(self, server_url: str):
        self.server_url: str = server_url

    def fetch_actions(self, obs: dict) -> list[dict]:
        payload = self._map_obs_to_payload(obs)

        try:
            response = requests.post(self.server_url, json=payload, timeout=10)
            response.raise_for_status()
            actions = self._map_response_to_actions(response.json())

            assert len(actions) != 0, "Response actions are not expected to be empty"
            return actions

        except requests.exceptions.RequestException as e:
            print(f"Failed to connect or fetch data: {e}")

        return []

    def _map_obs_to_payload(self, obs: dict) -> dict:

        payload = {
            "encoded": json_numpy.dumps(
                {
                    "full_image": obs["cam_external"],
                    "state": np.hstack((obs["arm_angles"], obs["gripper"])),
                    "instruction": "place the red block on the green block",
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
                    "gripper": np.array(row[6], dtype=np.uint8),
                }
            )

        return actions
