from .controller import ICommand, IANCController

"""
Command pattern: https://refactoring.guru/design-patterns/command .
Point of the pattern is encapsulation, nothing crazy.
In our case, we don't want to tightly couple certain actions to certain UI prompts.
Maybe we want the Atom button to invoke a certain command instead of using console input.
Command pattern makes them easily to swap out.
Not sure if it is implemented properly though.
"""

class ExitCommand(ICommand):
    def execute(self) -> None:
        exit(1) # Or should gracefully be 0?

class ListCommandsCommand(ICommand):
    def __init__(self, command_mapping: dict[str, ICommand]) -> None:
        self.command_mapping: dict[str, ICommand] = command_mapping

    def execute(self) -> None:
        print(self.command_mapping.keys())

class StopCommand(ICommand):
    def __init__(self, anc_controller: IANCController) -> None:
        self.anc_controller = anc_controller

    def execute(self) -> None:
        self.anc_controller.stop()

class StartDragRecordCommand(ICommand):
    """Should change state to DragRecord"""
    def __init__(self, anc_controller: IANCController) -> None:
        self.anc_controller = anc_controller

    def execute(self) -> None:
        self.anc_controller.start_drag_record()

class ReplayRecordCommand(ICommand):
    def __init__(self, anc_controller: IANCController) -> None:
        self.anc_controller = anc_controller

    def execute(self) -> None:
        self.anc_controller.start_replay_record()


