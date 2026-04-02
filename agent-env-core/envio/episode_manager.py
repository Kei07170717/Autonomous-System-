from abc import ABC, abstractmethod

from agent.agent import ReplayAgent
from core.interfaces import Agent
from core.types import Action


class IActionSequenceManager(ABC):
    """
    Used for retrieving action sequences produced by DragRecordingState (IActionSequenceWriter).
    """
    @abstractmethod
    def is_episode_recorded(self) -> bool:
        pass

    @abstractmethod
    def get_actions(self) -> list[dict]:
        pass

    @abstractmethod
    def set_actions(self, actions: list[dict]) -> None:
        pass

    @abstractmethod
    def clear_actions(self):
        pass

    @abstractmethod
    def create_replay_agent(self) -> Agent:
        pass
        

class ActionSequenceManager(IActionSequenceManager):
    
    def __init__(self):
        self.actions: list[dict] = []
        # self.is_episode_recorded = 

    def is_episode_recorded(self) -> bool:
        return len(self.actions) > 0

    def get_actions(self) -> list[dict]:
        return self.actions

    def set_actions(self, actions: list[dict]) -> None:
        self.actions = actions # Or clear and append self list?

    def clear_actions(self):
        self.actions.clear()

    def create_replay_agent(self) -> Agent:
        # print("Created replay agent with actions len: ", len(self.actions))
        return ReplayAgent(self.actions)
        
