from controller import ANCController
from controller.controller import IANCController
from core.interfaces import (
    CameraSensorModule,
    IArmActuator,
    IBody,
    IGripperActuator,
    IJointAnglesSensor,
    IObserver,
    IResettable,
    JointAnglesSensorModule,
    SensorModule,
)
from environment import Body, Observer
from hardware.camera import Camera
from hardware.dummy_components import DummyComponent
from hardware.my_cobot_280pi_adapter import MyCobot280PiAdapter
from ui import ANCConsoleUI
import argparse


if __name__ == "__main__":
    print("Starting agent-env-core")
    parser = argparse.ArgumentParser()

    parser.add_argument(
            "--live",
            action="store_true"
            )

    parser.add_argument(
        "--camera-id", 
        type=str, 
        default="USB 2.0 Camera: USB Camera", 
        help="The name of the camera to use."
    )

    args = parser.parse_args()

    dummy_component: DummyComponent = DummyComponent()
    arm_sensor: IJointAnglesSensor = dummy_component
    arm_actuator: IArmActuator = dummy_component
    gripper_actuator: IGripperActuator = dummy_component
    resettable: IResettable = dummy_component
   
    # Override with live components if enabled
    if args.live:
        cobot_adapter = MyCobot280PiAdapter()
        arm_sensor = cobot_adapter
        arm_actuator = cobot_adapter
        resettable = cobot_adapter

    drag_body: IBody = Body(
        arm_sensor=arm_sensor,
        arm_actuator=dummy_component,
        gripper_actuator=dummy_component,
    )

    camera1_id: str = "USB 2.0 Camera: USB Camera" # CHANGE TO ACTUAL NAME
    # sensor_modules: [SensorModule]
    observer: IObserver = Observer(
        [
            # CameraSensorModule(id="Cam1", camera_sensor=Camera(camera1_id)),
            JointAnglesSensorModule(
                id="arm_angles", joint_angles_sensor=arm_sensor
            )
        ]
    )

    controller: ANCController = ANCController(drag_body=drag_body, observer=observer, resettable=resettable)
    ui: ANCConsoleUI = ANCConsoleUI(controller)
    ui.start()
