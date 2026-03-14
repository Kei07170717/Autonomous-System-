from __future__ import annotations
from ..base_state import State
from . import reset

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..controller import ANCController

class ReplayRecordingState(State):
    """
    This state is meant for running the replay of KinestheticAgent recorded
    actions. It should have the actual Body without dummy components. The Observer
    is assumed to be composed of camera(s) and the JointAngles sensor. This state 
    should have a ReplayAgent which sends the actions from a file to the RecordedEnvironment.
    """
  
    def __init__(self, context: ANCController):
        super().__init__(context, state_name="ReplayRecording")
        assert self.context.live_body is not None

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
        self.context.set_state(reset.ResettingState(self.context))
