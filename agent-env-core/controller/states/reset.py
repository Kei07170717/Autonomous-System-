from __future__ import annotations
from typing import TYPE_CHECKING
# State pattern is clunky with python, this solves some circular dependency problems
if TYPE_CHECKING:
    from ..controller import ANCController

# from ..controller import ANCController
from ..base_state import State
# from ..interfaces import State
from ..utils import disabled_in_this_state
from .idle import IdlingState

# _STATE_NAME = "Resetting"



from ..base_state import State


class ResettingState(State):
  
    def __init__(self, context: ANCController):
        super().__init__(context, state_name="Resetting")
        # self._dummy_state = 0

    def execute(self):
        # if self._dummy_state > 10:
        #     self.context.set_state(IdlingState(self.context))
        # self._dummy_state += 1
        if not self.context.resettable:
            print("a")
            return

        if self.context.resettable.is_reset():
            self.context.set_state(IdlingState(self.context))
        else:
            self.context.resettable.reset()

    @disabled_in_this_state
    def open_gripper(self):
        pass

    @disabled_in_this_state
    def close_gripper(self):
        pass

    @disabled_in_this_state
    def start_replay_record(self):
        pass

    # def stop_replay_record(self):
    #     pass

    @disabled_in_this_state
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
