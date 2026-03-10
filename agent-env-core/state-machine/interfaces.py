from abc import ABC, abstractmethod

class IANCController(ABC):

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

    @abstractmethod
    def start_inference(self):
        pass

    @abstractmethod
    def stop_inference(self):
        pass

class State(ABC):
    def __init__(self, context: IANCController):
        self.context: IANCController = context

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

    @abstractmethod
    def start_inference(self):
        pass

    @abstractmethod
    def stop_inference(self):
        pass
