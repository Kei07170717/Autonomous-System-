from abc import ABC, abstractmethod
from ..interfaces import IANCController

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

    # @abstractmethod
    # def stop_replay_record(self):
    #     pass

    @abstractmethod
    def start_drag_record(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    # @abstractmethod
    # def stop_drag_record(self):
    #     pass

    # @abstractmethod
    # def start_inference(self):
    #     pass
    #
    # @abstractmethod
    # def stop_inference(self):
    #     pass
