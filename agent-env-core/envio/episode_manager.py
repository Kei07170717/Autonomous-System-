from abc import ABC, abstractmethod

from core.types import Action


class IActionSequenceManager(ABC):
    """
    Used for retrieving action sequences produced by DragRecordingState (IActionSequenceWriter).
    """
    @abstractmethod
    def is_episode_recorded(self) -> bool:
        pass

    @abstractmethod
    def get_actions(self) -> list[Action]:
        pass

    @abstractmethod
    def set_actions(self, actions: list[Action]) -> None:
        pass

    @abstractmethod
    def clear_actions(self):
        pass

class ActionSequenceManager(IActionSequenceManager):
    
    def __init__(self):
        self.actions: list[Action] = []
        # self.is_episode_recorded = 

    def is_episode_recorded(self) -> bool:
        return len(self.actions) > 0

    def get_actions(self) -> list[Action]:
        return self.actions

    def set_actions(self, actions: list[Action]) -> None:
        self.actions = actions # Or clear and append self list?

    def clear_actions(self):
        self.actions.clear()
