from typing import Tuple, Optional, Sequence, Union #maybe sequence
from dataclasses import dataclass
import numpy as np
from numpy._typing import DTypeLike

@dataclass(frozen=True) #dataclass instances remain immutable
class Action:
    arm: list[float]
    # While the optional makes sense, gripper vals are always generated
    # for our lora. This is a problematic dependency, but hard to
    # currently work around.
    # gripper: Optional[int] = None 
    gripper: int

@dataclass(frozen=True)
class TensorSpec:
    shape: Tuple[int, ...]
    dtype: DTypeLike

SpecTree = Union[TensorSpec, dict[str, 'SpecTree']]
