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
        self.execution_step = 0  # Replaces 'current_step'. Only increments on valid actions.
        self.ensemble_buffer = defaultdict(list)
        self.buffer_lock = threading.Lock()

        # Async Fetching State
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.fetch_future = None

        # Fallback tracking
        self.virtual_target_angles = None
        self.last_gripper_act = None

    def get_action(self, obs: dict) -> dict:
        # Initialize tracking on the very first observation
        if self.virtual_target_angles is None:
            self.virtual_target_angles = obs["arm_angles"].copy()
            # Map the initial observation to a strict 0 or 1 for the first fallback
            self.last_gripper_act = 1 if obs["gripper"] < 90 else 0 

        # 1. Non-blocking Fetch: Pass the current *execution step* if self.fetch_future is None or self.fetch_future.done():
            self.fetch_future = self.executor.submit(
                self._fetch_actions_async, obs.copy(), self.execution_step
            )

        # 2. Retrieve ensembled action for the current step
        # Block only on the very first step to wait for the first chunk
        action_delta = self._pop_ensembled_action(wait=(self.execution_step == 0))

        # 3. Handle Buffer Underruns (Latency Spikes)
        if action_delta is None:
            # We are starving. Output a fallback action, but DO NOT increment execution_step.
            # The robot pauses in time until the actions arrive.
            print(f"[Warning] Buffer underrun at step {self.execution_step}. Holding position.")
            return {
                "arm_angles": self.virtual_target_angles if self.use_virtual_target else obs["arm_angles"],
                "gripper": self.last_gripper_act # Safe binary fallback
            }

        # 4. Apply Actions 
        base_arm_angles = self.virtual_target_angles if self.use_virtual_target else obs["arm_angles"]

        next_action = {
            "arm_angles": base_arm_angles + action_delta["arm_angles"],
            "gripper": action_delta["gripper"]
        }

        # Update persistent state for the next iteration
        if self.use_virtual_target:
            self.virtual_target_angles = next_action["arm_angles"].copy()
            
        self.last_gripper_act = next_action["gripper"]
        
        # 5. Advance the clock ONLY because we successfully applied an action
        self.execution_step += 1

        return next_action

    def _fetch_actions_async(self, obs: dict, request_step: int):
        actions = self.remote_action_provider.fetch_actions(obs)

        if not actions:
            return

        with self.buffer_lock:
            for i, action in enumerate(actions):
                target_step = request_step + i
                
                # Because execution_step pauses during stalls, target_step will 
                # correctly align with the unexecuted future steps once they arrive.
                if target_step >= self.execution_step:
                    self.ensemble_buffer[target_step].append(action)

    def _pop_ensembled_action(self, wait: bool = False) -> dict | None:
        if wait:
            while True:
                with self.buffer_lock:
                    if len(self.ensemble_buffer[self.execution_step]) > 0:
                        break
                time.sleep(0.01)

        with self.buffer_lock:
            actions_for_step = self.ensemble_buffer.pop(self.execution_step, [])
            
            # Clean up stale memory
            stale_keys = [k for k in list(self.ensemble_buffer.keys()) if k < self.execution_step]
            for k in stale_keys:
                del self.ensemble_buffer[k]

        if not actions_for_step:
            return None # Triggers the underrun hold

        # Continuous Ensembling for Arm Angles
        avg_arm_angles = np.mean([a["arm_angles"] for a in actions_for_step], axis=0)
        
        # Binary Majority Vote for the Gripper
        gripper_mean = np.mean([a["gripper"] for a in actions_for_step])
        ensembled_gripper = 1 if gripper_mean >= 0.5 else 0

        return {
            "arm_angles": avg_arm_angles,
            "gripper": int(ensembled_gripper)
        }
