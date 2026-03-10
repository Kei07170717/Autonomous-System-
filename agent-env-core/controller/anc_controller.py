from .interfaces import IANCController, State
from states.reset import ResettingState
import time


class ANCController(IANCController):
    def __init__(self):
        self.state: State = ResettingState(self)
        pass

    def run_loop(self):
        for _ in range(5):
            time.sleep(0.1)

    def open_gripper(self):
        pass

    def close_gripper(self):
        pass

    def start_replay_record(self):
        pass

    def stop_replay_record(self):
        pass

    def start_drag_record(self):
        pass

    def stop_drag_record(self):
        pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass
