from typing import Optional, Sequence #maybe sequence
from dataclasses import dataclass

@dataclass(frozen=True) #dataclass instances remain immutable
class Action:
    arm: list[float]
    # While the optional makes sense, gripper vals are always generated
    # for our lora. This is a problematic dependency, but hard to
    # currently work around.
    # gripper: Optional[int] = None 
    gripper: int

