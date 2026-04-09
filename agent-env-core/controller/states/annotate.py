from __future__ import annotations
from typing import TYPE_CHECKING

# from controller.states import replay_record

from . import drag_record

if TYPE_CHECKING:
    from ..controller import ANCController

from ..base_state import State

# TODO: migrate annotating to this state? (currently callback in BaseWriter)
class AnnotateState(State):
  
    def __init__(self, context: ANCController):
        super().__init__(context, state_name="Annotating")

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

    # def start_replay_record(self):
    #     pass
    #
    # def start_drag_record(self):
    #     pass

    def stop(self):
        pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass
