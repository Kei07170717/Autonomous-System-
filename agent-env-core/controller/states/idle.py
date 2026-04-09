from __future__ import annotations
from typing import TYPE_CHECKING

from controller.states import replay_record

from . import drag_record

if TYPE_CHECKING:
    from ..controller import ANCController

from ..base_state import State

class IdlingState(State):
  
    def __init__(self, context: ANCController):
        super().__init__(context, state_name="Idling", color= ( "green", 213,232, 212))

    def on_state_enter(self):
        super().on_state_enter()
        pass

    def on_state_exit(self):
        pass

    def execute(self):
        pass

    #def open_gripper(self):
     #   pass

    #def close_gripper(self):
     #   pass

    def start_replay_record(self):
        self.context.set_state(replay_record.ReplayRecordingState(self.context))

    def start_drag_record(self):
        self.context.set_state(drag_record.DragRecordingState(self.context))


    def stop(self):
        pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass
