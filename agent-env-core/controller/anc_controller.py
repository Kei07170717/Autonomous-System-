from .interfaces import IANCController, State
from .states import ResettingState
from environment import IBody, Body
import time


class ANCController(IANCController):
    def __init__(self, ):
        print("Entering Resetting state")
        self.state: State = ResettingState(self)
        self.terminating: bool = False

    def set_state(self, state: State) -> None:
        print("Entering {} state".format(state.get_state_name()))
        self.state = state

    def run_loop(self):
        while not self.terminating:
            self.state.execute()
            time.sleep(0.1) # TODO: Remove

    def open_gripper(self):
        self.state.open_gripper()

    def close_gripper(self):
        self.state.close_gripper()

    def start_replay_record(self):
        self.state.start_replay_record()

    # def stop_replay_record(self):
    #     pass

    def start_drag_record(self):
        self.state.start_drag_record()

    def stop(self):
        self.state.stop()

    # def stop_drag_record(self):
    #     pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass
