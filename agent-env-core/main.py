from controller.interfaces import IANCController
from controller import ANCController

if __name__ == "__main__":
    print("Starting agent-env-core")
    controller: IANCController = ANCController()
    controller.run_loop()

