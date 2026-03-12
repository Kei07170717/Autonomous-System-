from controller.interfaces import IANCController
from controller import ANCController
from hardware.dummy_components import DummyComponent
from ui import ANCConsoleUI
from core.interfaces import IArmActuator, IJointAnglesSensor, IGripperActuator, IBody
from environment import Body
from hardware.my_cobot_280pi_adapter import MyCobot280PiAdapter

if __name__ == "__main__":
    print("Starting agent-env-core")
    # cobot_adapter = MyCobot280PiAdapter()
    
    # drag_body: IBody
    dummy_component: DummyComponent = DummyComponent()

    drag_body: IBody = Body(
            arm_sensor=dummy_component,
            arm_actuator=dummy_component,
            gripper_actuator=dummy_component
            )

    controller: IANCController = ANCController(
            drag_body=drag_body)
    ui: ANCConsoleUI = ANCConsoleUI(controller)
    ui.start()

