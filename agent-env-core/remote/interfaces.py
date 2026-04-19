from abc import ABC, abstractmethod


class IRemoteActionProvider(ABC):
    # def __init__(self):
    #     super().__init__()

    @abstractmethod
    def fetch_actions(self, obs: dict) -> list[dict]:
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        pass

