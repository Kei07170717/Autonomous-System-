from .interfaces import ICommand, IANCController

class ExitCommand(ICommand):
    def execute(self) -> None:
        exit(1) # Or should gracefully be 0?

class ListCommandsCommand(ICommand):
    def __init__(self, command_mapping: dict[str, ICommand]) -> None:
        self.command_mapping: dict[str, ICommand] = command_mapping

    def execute(self) -> None:
        print(self.command_mapping.keys())

class StartDragRecordCommand(ICommand):
    """Should change state to DragRecord"""
    def __init__(self) -> None:
        pass 

    def execute(self) -> None:
        print("StartDrag command not implemented yet")
        pass

# class ReplayCommand(ICommand):
#     def execute(self) -> None:
#         pass
