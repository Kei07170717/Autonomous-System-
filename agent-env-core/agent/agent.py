from core.types import Action
from core.interfaces import Agent
import math
import numpy as np
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import time

from remote.interfaces import IRemoteActionProvider

class KinestheticAgent(Agent):
    '''This agent is passive. This agent is used for gathering 'drag&record' data,
    which can later be replayed through another agent. The environment should
    not execute actions using this agent.'''
    def __init__(self) -> None:
        super().__init__()
        self.explicit_gripper_val: int | None = None

    def get_action(self, obs: dict) -> dict:
        
        if self.explicit_gripper_val is not None:
            final_gripper_val = self.explicit_gripper_val
        else:
            final_gripper_val = 0 if obs["gripper"] > 90 else 1 # TODO: remove this dependency 
        return {"arm_angles": obs["arm_angles"], 
                "gripper": final_gripper_val
                } # Hardcoding these keys is bad!!!

    def set_griper_manually(self, explicit_gripper_val: int):
        self.explicit_gripper_val = explicit_gripper_val


class RotatingAgent(Agent):
    '''This agent safely rotates a specific joint back and forth.
    It uses a sine wave to guarantee smooth, bounded movements, 
    preventing erratic jumps or cable tangling on the MyCobot280PI.'''

    def __init__(self, joint_index: int = 0, amplitude: float = 30.0, speed: float = 0.05):
        """
        Args:
            joint_index: Which joint to rotate (0-5, where 0 is the base).
            amplitude: Maximum rotation angle from the zero position. 
                       Keep this small (e.g., 30 degrees) for safety.
            speed: How fast the sine wave progresses per step.
        """
        self.joint_index = joint_index
        self.amplitude = amplitude
        self.speed = speed
        self.step = 0

    def get_action(self, obs: dict) -> dict:
        # Calculate a smooth, bounded angle using $A \cdot \sin(\omega \cdot t)$
        current_angle = self.amplitude * math.sin(self.speed * self.step)
        
        # Advance the time step
        self.step += 1
        
        # Initialize all 6 joints to a safe, neutral 0.0 position
        target_angles = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        
        # Apply the safe rotation to the specified joint
        target_angles[self.joint_index] = current_angle
        
        return {"arm_angles": target_angles, "gripper": np.uint8(0)}


class ReplayAgent(Agent):
    """
    Simple agent that iterates over given actions.
    Usefull for replaying recordings.
    """
    def __init__(self, actions: list[dict]):
        self.actions: list[dict] = actions
        self.action_iter = iter(self.actions)

    def get_action(self, obs: dict) -> dict:
        return next(self.action_iter)
        

class MediatorAgent(Agent):
    def __init__(self, remote_action_provider: IRemoteActionProvider, use_virtual_target: bool = False):
        self.remote_action_provider = remote_action_provider
        self.use_virtual_target = use_virtual_target

        # Temporal Ensembling State
        self.current_step = 0
        self.ensemble_buffer = defaultdict(list)
        self.buffer_lock = threading.Lock()

        # Async Fetching State
        # Using a single worker ensures we don't spam the API with concurrent requests
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.fetch_future = None

        # Virtual Target State
        self.virtual_target_angles = None

    def get_action(self, obs: dict) -> dict:
        # Initialize virtual target on the very first observation
        if self.virtual_target_angles is None:
            self.virtual_target_angles = obs["arm_angles"].copy()

        # 1. Non-blocking Fetch: If no fetch is running, dispatch one in the background
        if self.fetch_future is None or self.fetch_future.done():
            # Pass a copy of obs and the *current* step so the background thread 
            # knows exactly which timesteps this new chunk belongs to.
            self.fetch_future = self.executor.submit(
                self._fetch_actions_async, obs.copy(), self.current_step
            )

        # 2. Retrieve ensembled action for the current step
        # We only block on the very first step (to let the initial chunk arrive)
        action_delta = self._pop_ensembled_action(wait=(self.current_step == 0))

        # 3. Handle Buffer Underruns (Latency Spikes)
        if action_delta is None:
            print(f"[Warning] Buffer underrun at step {self.current_step}. Holding position.")
            action_delta = {
                "arm_angles": np.zeros_like(obs["arm_angles"]),
                "gripper": obs["gripper"] # Fallback to keeping gripper as is
            }

        # 4. Apply Actions (Real vs Virtual Target)
        if self.use_virtual_target:
            # Actions accumulate on top of our perfect "virtual" tracking target
            base_arm_angles = self.virtual_target_angles
        else:
            # Actions apply directly to noisy real-world observation
            base_arm_angles = obs["arm_angles"]

        next_action = {
            "arm_angles": base_arm_angles + action_delta["arm_angles"],
            "gripper": action_delta["gripper"] # Treated as absolute value
        }

        # Update virtual target for the next loop iteration
        if self.use_virtual_target:
            self.virtual_target_angles = next_action["arm_angles"].copy()

        self.current_step += 1
        return next_action

    def _fetch_actions_async(self, obs: dict, request_step: int):
        """Runs in a background thread to prevent blocking the 10Hz loop."""
        actions = self.remote_action_provider.fetch_actions(obs)

        if not actions:
            return

        with self.buffer_lock:
            for i, action in enumerate(actions):
                target_step = request_step + i
                
                # Only queue actions for steps we haven't executed yet.
                # Because inference takes ~0.7s (7 steps), the first 7 actions
                # in this chunk will likely be discarded as they are in the past.
                if target_step >= self.current_step:
                    self.ensemble_buffer[target_step].append(action)

    def _pop_ensembled_action(self, wait: bool = False) -> dict | None:
        """Safely extracts and averages overlapping actions for the current step."""
        if wait:
            # Block and wait for the API (only happens at step 0)
            while True:
                with self.buffer_lock:
                    if len(self.ensemble_buffer[self.current_step]) > 0:
                        break
                time.sleep(0.01)

        with self.buffer_lock:
            actions_for_step = self.ensemble_buffer.pop(self.current_step, [])
            
            # Clean up stale memory (just in case steps were skipped)
            stale_keys = [k for k in self.ensemble_buffer.keys() if k < self.current_step]
            for k in stale_keys:
                del self.ensemble_buffer[k]

        if not actions_for_step:
            return None # Signals a buffer underrun

        # 1. Continuous Ensembling for Arm Angles
        avg_arm_angles = np.mean([a["arm_angles"] for a in actions_for_step], axis=0)
        
        # 2. Binary Majority Vote for the Gripper
        # Taking the mean of 0s and 1s gives the percentage of "close" predictions.
        # If >= 0.5, the majority voted to close (1). Otherwise, open (0).
        gripper_mean = np.mean([a["gripper"] for a in actions_for_step])
        ensembled_gripper = 1 if gripper_mean >= 0.5 else 0

        return {
            "arm_angles": avg_arm_angles,
            "gripper": int(ensembled_gripper) # Cast to int to ensure strict binary 0 or 1
        }
