import argparse

import envlogger
import tensorflow as tf
import tensorflow_datasets as tfds
from envlogger.backends import tfds_backend_writer

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
    GripperSensorModule,
    IGripperSensor,
    IColorChanger
)
from envio import dataset_storage_manager
from envio.dataset_storage_manager import DatasetStorageManager, IDatasetStorageManager
from environment import Body, Observer
from hardware.camera import Camera
from hardware.dummy_components import DummyComponent
from hardware.my_cobot_280pi_adapter import MyCobot280PiAdapter
from ui import ANCConsoleUI

# def setup_and_parse_arguments()

if __name__ == "__main__":
    print("Starting agent-env-core")
    parser = argparse.ArgumentParser()

    parser.add_argument("--live", action="store_true")

    parser.add_argument(
        "--hz",
        type=int,
        default=20,
        help="Hz that the controller will operate on; 10hz is 10 send_angles a second.",
    )

    parser.add_argument(
        "--camera-id",
        type=str,
        default="USB 2.0 Camera: USB Camera",
        help="The name of the camera to use.",
    )

    args = parser.parse_args()

    dummy_component: DummyComponent = DummyComponent()
    arm_sensor: IJointAnglesSensor = dummy_component
    arm_actuator: IArmActuator = dummy_component
    gripper_actuator: IGripperActuator = dummy_component
    gripper_sensor: IGripperSensor = dummy_component
    resettable: IResettable = dummy_component
    color_changer: IColorChanger = dummy_component
    
    # Override with live components if enabled
    if args.live:
        cobot_adapter = MyCobot280PiAdapter()
        arm_sensor = cobot_adapter
        arm_actuator = cobot_adapter
        resettable = cobot_adapter
        gripper_sensor = cobot_adapter
        gripper_actuator = cobot_adapter
        color_changer = cobot_adapter

    drag_body: IBody = Body(
        arm_sensor=arm_sensor,
        arm_actuator=dummy_component,
        gripper_actuator=dummy_component,
    )

    live_body: IBody = Body(
        arm_sensor=arm_sensor,
        arm_actuator=arm_actuator,
        gripper_actuator=gripper_actuator,
    )

    # sensor_modules: [SensorModule]
    observer: IObserver = Observer(
        [
            JointAnglesSensorModule(
                id="arm_angles", joint_angles_sensor = arm_sensor
            ),
            GripperSensorModule(
                id = "gripper", gripper_sensor = gripper_sensor
            )
        ]
    )
    # conf = get_dataset_config()
    # writer = get_writer(conf)

    # Quick and dirty
    try:
        cam1 = Camera(camera_name=args.camera_id)
        observer.attach_sensor_module(CameraSensorModule(id="cam1", camera_sensor=cam1))
    except Exception as e:
        print("Couldn't init camera, most likely wrong path: ", args.camera_id)

    ### WRITING BACKEND
    dataset_storage_manager: IDatasetStorageManager = DatasetStorageManager()
    dataset_destination_path: str = dataset_storage_manager.create_new_dataset_directory()
    dataset_config = tfds.rlds.rlds_base.DatasetConfig(
        name="my_imitation_dataset",
        observation_info=tfds.features.FeaturesDict(
            {"arm_angles": tfds.features.Tensor(shape=(6,), dtype=tf.float32),
             "gripper": tf.uint8}
        ),
        action_info=tfds.features.FeaturesDict(
            {
                "arm_angles": tfds.features.Tensor(shape=(6,), dtype=tf.float32),
                "gripper": tfds.features.Tensor(shape=(), dtype=tf.uint8),
            }
        ),
        # RLDS strictly expects reward and discount fields, even for imitation learning.
        reward_info=tf.float32,
        discount_info=tf.float64,  # Forced to use 64bits for some reason, TODO: lower this?
    )
    dataset_writer = tfds_backend_writer.TFDSBackendWriter(
        data_directory=dataset_destination_path,
        split_name="train",
        max_episodes_per_file=20, # TODO: justify this number
        ds_config=dataset_config,
    )

    controller: ANCController = ANCController(
        drag_body=drag_body,
        observer=observer,
        arm_actuator=arm_actuator,
        resettable=resettable,
        live_body=live_body,
        hz=args.hz,
        writer=dataset_writer,
        color_changer = color_changer
    )
    ui: ANCConsoleUI = ANCConsoleUI(controller)
    ui.start()
