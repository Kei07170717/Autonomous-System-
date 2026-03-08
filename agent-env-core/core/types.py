from typing import Optional, Sequence #maybe sequence
from dataclasses import dataclass

@dataclass(frozen=True) #dataclass instances remain immutable
class Action:
    arm: list[float]
    gripper: Optional[int] = None

