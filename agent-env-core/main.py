from controller.interfaces import IANCController
from controller import ANCController
from ui import ANCConsoleUI

if __name__ == "__main__":
    print("Starting agent-env-core")
    controller: IANCController = ANCController()
    ui: ANCConsoleUI = ANCConsoleUI(controller)
    ui.start()

