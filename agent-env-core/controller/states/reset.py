from ..interfaces import IANCController
from .state import State
from .idle import IdlingState

# _STATE_NAME = "Resetting"

class ResettingState(State):
  
    def __init__(self, context: IANCController):
        super().__init__(context, state_name="Resetting")
        # self._dummy_state = 0

    def execute(self):
        # if self._dummy_state > 10:
        #     self.context.set_state(IdlingState(self.context))
        # self._dummy_state += 1
        pass

    def open_gripper(self):
        pass

    def close_gripper(self):
        pass

    def start_replay_record(self):
        pass

    # def stop_replay_record(self):
    #     pass

    def start_drag_record(self):
        pass

    def stop(self):
        pass

    # def stop_drag_record(self):
    #     pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass
