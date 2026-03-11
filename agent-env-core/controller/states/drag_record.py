from ..interfaces import IANCController, State

class DragRecordingState(State):
    """
    In this state, the arm should go limp and interaction between
    KinestheticAgent and a child class of RecordedEnvironment should happen.
    This makes it so that the interactions are recorded automatically. 
    This state is meant to be spawned from the IdlingState and transition to
    the ResettingState when done or terminated.
    """
  
    def __init__(self, context: IANCController):
        super().__init__(context, state_name="DragRecording")

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
