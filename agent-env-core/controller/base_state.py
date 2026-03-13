from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .controller import ANCController

class State(ABC):
    def __init__(self, context: ANCController, state_name: str = "Undefined"):
        self.state_name: str = state_name
        self.context: ANCController = context

    def get_state_name(self) -> str:
        return self.state_name

    @abstractmethod
    def execute(self):
        pass
    @abstractmethod
    def open_gripper(self):
        pass

    @abstractmethod
    def close_gripper(self):
        pass

    @abstractmethod
    def start_replay_record(self):
        pass

    # @abstractmethod
    # def stop_replay_record(self):
    #     pass

    @abstractmethod
    def start_drag_record(self):
        pass

    @abstractmethod
    def stop(self):
        pass
