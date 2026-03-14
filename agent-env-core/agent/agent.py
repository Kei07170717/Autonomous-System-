from core.types import Action
from core.interfaces import Agent
import math


class KinestheticAgent(Agent):
    '''This agent is passive. This agent is used for gathering 'drag&record' data,
    which can later be replayed through another agent. The environment should
    not execute actions using this agent.'''

    def get_action(self, obs: dict) -> Action:
        # TODO: return observed angles
        return Action([0, 0, 0, 0, 0, 0], 0)


# Vibe coded agent just for the sake of testing
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

    def get_action(self, obs: dict) -> Action:
        # Calculate a smooth, bounded angle using $A \cdot \sin(\omega \cdot t)$
        current_angle = self.amplitude * math.sin(self.speed * self.step)
        
        # Advance the time step
        self.step += 1
        
        # Initialize all 6 joints to a safe, neutral 0.0 position
        target_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Apply the safe rotation to the specified joint
        target_angles[self.joint_index] = current_angle
        
        # Return the joint angles and a closed/neutral gripper state (0)
        return Action(target_angles, 0)

