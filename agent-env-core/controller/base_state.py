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
    def on_state_enter(self):
        """
        Similar to init, but more safe since this can
        be ran after the previous state has exit.
        """
        pass

    @abstractmethod
    def on_state_exit(self):
        """
        Similar to destructor of current state.
        """
        pass

    @abstractmethod
    def execute(self):
        pass
    
    def open_gripper(self):
        self.context.live_body.set_gripper_open()

    
    def close_gripper(self):
        self.context.live_body.set_gripper_closed()

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

    @abstractmethod
    def take_ref_image(self):
        pass

