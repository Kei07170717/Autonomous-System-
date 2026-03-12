import time

from core.interfaces import IObserver
from environment import Body, IBody

from .interfaces import IANCController, State
from .states import ResettingState


class ANCController(IANCController):
    """
    This class controlls the program using states (state design pattern).
    The ANCController has its own loop and will delegate its corresponding 
    actions to the underlying states. ANCController can serve as a 'backbone'
    for a UI.
    It receives a drag_body and optionally a live_body. The drag_body is a 
    simply dummy body that doesn't do anything, even when sending actions.
    The live_body is composed of the actual actuators, sending an action will
    have impact on the environment and hence should be used for
    ReplayRecordingState or other automated motion states.
    """
    def __init__(self,
                 drag_body: IBody,
                 observer: IObserver,
                 live_body: IBody | None = None
                 ):
        self.drag_body: IBody | None = drag_body
        self.live_body: IBody | None = live_body
        print("Entering Resetting state")
        self.state: State = ResettingState(self)
        self.terminating: bool = False

    def set_state(self, state: State) -> None:
        print("Entering {} state".format(state.get_state_name()))
        self.state = state

    def run_loop(self):
        while not self.terminating:
            self.state.execute()
            time.sleep(0.1)  # TODO: Remove

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
