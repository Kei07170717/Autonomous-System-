from __future__ import annotations
from abc import ABC, abstractmethod

class IANCController(ABC):

    @abstractmethod
    def set_state(self, state: State):
        pass

    @abstractmethod
    def run_loop(self):
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

    @abstractmethod
    def stop_replay_record(self):
        pass

    @abstractmethod
    def start_drag_record(self):
        pass

    @abstractmethod
    def stop_drag_record(self):
        pass

    # @abstractmethod
    # def start_inference(self):
    #     pass
    #
    # @abstractmethod
    # def stop_inference(self):
    #     pass

class State(ABC):
    def __init__(self,  context: IANCController, state_name: str = "Undefined"):
        self.state_name: str = state_name
        self.context: IANCController = context

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

    @abstractmethod
    def stop_replay_record(self):
        pass

    @abstractmethod
    def start_drag_record(self):
        pass

    @abstractmethod
    def stop_drag_record(self):
        pass

    # @abstractmethod
    # def start_inference(self):
    #     pass
    #
    # @abstractmethod
    # def stop_inference(self):
    #     pass

class ICommand(ABC):

    @abstractmethod
    def execute(self) -> None:
        pass
