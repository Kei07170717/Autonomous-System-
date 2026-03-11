import threading

from controller.commands import *
from controller.interfaces import IANCController, ICommand
# from controller import ANCController
from controller.states import IdlingState, ResettingState  # SHOULDN't BE HERE

command_mapping: dict[str, ICommand] = {
        "exit": ExitCommand(),
        "start drag": StartDragRecordCommand()
        }

help_command = ListCommandsCommand(command_mapping)
command_mapping["help"] = help_command


class ANCConsoleUI:
    def __init__(self, anc_controller: IANCController) -> None:
        self.anc_controller: IANCController = anc_controller

    def start(self):
        # Spawn a separate thread for the ANCController (because the 
        # 'input()' method is a blocking call, it would block the entire program)
        self.controller_thread = threading.Thread(target=self.anc_controller.run_loop, daemon=True)
        self.controller_thread.start()

        while True:
            prompt = input("agent-env-core> ").strip().lower()
            
            command = command_mapping.get(prompt)

            # Don't run the command if it's not valid
            if command:
                command.execute()
            else:
                help_command.execute()


            # if cmd == "help":
            #     print("Possible commands: ")
            # elif cmd == "reset":
            #     self.anc_controller.set_state(ResettingState(self.anc_controller))
            # elif cmd == "idle":
            #     self.anc_controller.set_state(IdlingState(self.anc_controller))


        


