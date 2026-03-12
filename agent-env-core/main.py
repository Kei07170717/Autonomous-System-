from controller import ANCController
from controller.interfaces import IANCController
from core.interfaces import (
    CameraSensorModule,
    IArmActuator,
    IBody,
    IGripperActuator,
    IJointAnglesSensor,
    IObserver,
    JointAnglesSensorModule,
    SensorModule,
)
from environment import Body, Observer
from hardware.camera import Camera
from hardware.dummy_components import DummyComponent
from hardware.my_cobot_280pi_adapter import MyCobot280PiAdapter
from ui import ANCConsoleUI

if __name__ == "__main__":
    print("Starting agent-env-core")
    # cobot_adapter = MyCobot280PiAdapter()

    # drag_body: IBody
    dummy_component: DummyComponent = DummyComponent()

    drag_body: IBody = Body(
        arm_sensor=dummy_component,
        arm_actuator=dummy_component,
        gripper_actuator=dummy_component,
    )

    observer: IObserver = Observer(
        [
            # CameraSensorModule(id="Cam1", camera_sensor=Camera("1"))
            JointAnglesSensorModule(
                id="arm_angles", joint_angles_sensor=dummy_component
            )
        ]
    )

    controller: IANCController = ANCController(drag_body=drag_body, observer=observer)
    ui: ANCConsoleUI = ANCConsoleUI(controller)
    ui.start()
