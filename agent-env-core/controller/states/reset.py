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

    def execute(self):
        assert self.context.resettable is not None

        if self.context.resettable.is_reset():
            self.context.set_state(IdlingState(self.context))
            return


    def on_state_enter(self):
        """
        For this state, first check if we have an actual resettable instance or if it's already reset
        if so, just change to IdlingState. Otherwise call the reset method.
        """
        if self.context.resettable is None or self.context.resettable.is_reset():
            self.context.set_state(IdlingState(self.context))
            return
        else:
            self.context.resettable.reset()

    def on_state_exit(self):
        pass

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

    @disabled_in_this_state
    def take_ref_image(self):
        pass

    # def stop_drag_record(self):
    #     pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass
