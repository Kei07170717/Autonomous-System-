from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple
import numpy as np

from core.interfaces import BaseWriter
from core.types import Action

class IActionSequenceWriter(ABC):
    def __init__(self, metadata: Optional[dict[str, Any]] = None) -> None:
        self.metadata = metadata

    @abstractmethod
    def write_metadata(self):
        pass

    @abstractmethod
    def write_episode(self, steps: list):
        pass

    # @abstractmethod
    # def write_step(self, action, observation):
    #     pass

    # @abstractmethod
    # def open(self):
    #     pass
    #
    # @abstractmethod
    # def close(self):
    #     pass


# _ACTION_INDEX_IN_STEP = 1 # bad, should be struct(?) (now it depends on Recorder)
class NumpyActionSequenceWriter(IActionSequenceWriter):
    def __init__(
        self, 
        write_path: str,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(metadata)
        self.write_path: str = write_path

    def write_metadata(self):
        pass

    def write_episode(self, steps: list[dict]):
        print("Writing with steps length: ", len(steps))
        # print("Step 0: ", steps[0])
        # print(type(steps[0][0]), type(steps[0][1])) 
        actions: list[list[float]] = [step["arm_angles"] for step in steps] # TODO: add gripper
        np.savetxt(self.write_path, np.asarray(actions), delimiter=",")


# class RLDSWriterAdapter(BaseWriter):
#     def __init__(self, obs_spec, action_spec, metadata=None) -> None:
#         super().__init__(obs_spec, action_spec, metadata)

