from ..interfaces import IANCController, State

# _STATE_NAME = "Idling"

class IdlingState(State):
  
    def __init__(self, context: IANCController):
        super().__init__(context, state_name="Idling")

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
