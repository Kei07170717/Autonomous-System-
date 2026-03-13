from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controller import ANCController

from ..base_state import State

class IdlingState(State):
  
    def __init__(self, context: ANCController):
        super().__init__(context, state_name="Idling")

    def on_state_enter(self):
        pass

    def on_state_exit(self):
        pass

    def execute(self):
        pass

    def open_gripper(self):
        pass

    def close_gripper(self):
        pass

    def start_replay_record(self):
        pass

    def start_drag_record(self):
        pass

    def stop(self):
        pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass
