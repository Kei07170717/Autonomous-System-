from ..interfaces import State, IANCController

class ResettingState(State):
  
    def __init__(self, context: IANCController):
        super().__init__(context)

    def execute(self):
        pass

    def open_gripper(self):
        pass

    def close_gripper(self):
        pass

    def start_replay_record(self):
        pass

    def stop_replay_record(self):
        pass

    def start_drag_record(self):
        pass

    def stop_drag_record(self):
        pass

    # def start_inference(self):
    #     pass
    #
    # def stop_inference(self):
    #     pass
