import argparse
from typing import cast

from numpy._core.numeric import dtype
from numpy._typing import DTypeLike

from config import MyCobot280PIObserverBuilder, SemiDummyObserverBuilder

from controller import ANCController
from controller.controller import IANCController
from core.interfaces import (
    BaseWriter,
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
    IGripperSensor
)
from core.types import SpecTree, TensorSpec
from envio.dataset_storage_manager import DatasetStorageManager, IDatasetStorageManager
from envio.writing import DummyWriter, HDF5Writer
from environment import Body, Observer
from hardware.camera import Camera
from hardware.dummy_components import DummyComponent
from hardware.my_cobot_280pi_adapter import MyCobot280PiAdapter
from ui import ANCConsoleUI
import numpy as np

def get_simple_action_spec() -> SpecTree:
    return {
            "arm_angles": TensorSpec(shape=(6,), dtype=np.float32),
            "gripper": TensorSpec(shape=(), dtype=np.uint8)
            }

# def setup_and_parse_arguments()
def create_writer(writer_type: str, obs_spec: SpecTree, dataset_storage_manager: IDatasetStorageManager) -> BaseWriter | None:
    obs_spec = obs_spec
    action_spec = get_simple_action_spec()
    if writer_type == "hdf5":
        # TODO: return hdf5
        return HDF5Writer(obs_spec, action_spec, dataset_storage_manager) # TODO: temporary debugging..
    # elif writer_type == "rlds":
    #     try:
    #         import tensorflow as tf
    #         import tensorflow_datasets as tfds
    #         from envlogger.backends import tfds_backend_writer

    # dataset_config = tfds.rlds.rlds_base.DatasetConfig(
    #     name="my_imitation_dataset",
    #     observation_info=tfds.features.FeaturesDict(
    #         {"arm_angles": tfds.features.Tensor(shape=(6,), dtype=tf.float32),
    #          "gripper": tf.uint8}
    #     ),
    #     action_info=tfds.features.FeaturesDict(
    #         {
    #             "arm_angles": tfds.features.Tensor(shape=(6,), dtype=tf.float32),
    #             "gripper": tfds.features.Tensor(shape=(), dtype=tf.uint8),
    #         }
    #     ),
    #     # RLDS strictly expects reward and discount fields, even for imitation learning.
    #     reward_info=tf.float32,
    #     discount_info=tf.float64,  # Forced to use 64bits for some reason, TODO: lower this?
    # )
    # dataset_writer = tfds_backend_writer.TFDSBackendWriter(
    #     data_directory=dataset_destination_path,
    #     split_name="train",
    #     max_episodes_per_file=20, # TODO: justify this number
    #     ds_config=dataset_config,
    # )
    #     except ImportError as e:
    #         print("")
    #         raise e
    return None


if __name__ == "__main__":
    print("Starting agent-env-core")
    parser = argparse.ArgumentParser()

    parser.add_argument("--live", action="store_true")

    parser.add_argument(
        "--hz",
        type=int,
        default=10, # Can definitely get this higher if we spend time optimizing the controlloop
        help="Hz that the controller will operate on; 10hz is 10 send_angles a second.",
    )

    parser.add_argument(
        "--external-cam-id",
        type=str,
        default="USB 2.0 Camera: USB Camera",
        help="The name of the external camera to use.",
    )
    
    parser.add_argument(
        "--wrist-cam-id",
        type=str,
        default="USB 2.0 Camera: USB 2.0 Camera",
        help="The name of the wrist camera to use.",
    )

    # TODO: add options..
    parser.add_argument(
            "--writer",
            type=str,
            default="hdf5",
            help="Type of writer for the recording replay."
            )

    args = parser.parse_args()

    dummy_component: DummyComponent = DummyComponent()
    arm_sensor: IJointAnglesSensor = dummy_component
    arm_actuator: IArmActuator = dummy_component
    gripper_actuator: IGripperActuator = dummy_component
    gripper_sensor: IGripperSensor = dummy_component
    resettable: IResettable = dummy_component

    observer_builder = SemiDummyObserverBuilder()
    
    # Override with live components if enabled
    if args.live:
        cobot_adapter = MyCobot280PiAdapter()
        observer_builder = MyCobot280PIObserverBuilder(cobot_adapter)
        arm_sensor = cobot_adapter
        arm_actuator = cobot_adapter
        resettable = cobot_adapter
        gripper_sensor = cobot_adapter
        gripper_actuator = cobot_adapter

    observer_builder.register_joint_angles_sensor()
    observer_builder.register_gripper_sensor_module()
    observer_builder.build_and_register_camera_module("cam_external", args.external_cam_id)
    observer_builder.build_and_register_camera_module("cam_wrist", args.wrist_cam_id)
    observer = observer_builder.get_observer()
    obs_spec = observer_builder.get_observation_spec()

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


    ### WRITING BACKEND
    dataset_storage_manager: IDatasetStorageManager = DatasetStorageManager()
    # dataset_destination_path: str = dataset_storage_manager.create_new_dataset_directory()
    dataset_writer: BaseWriter | None = create_writer(args.writer, obs_spec, dataset_storage_manager)

    controller: ANCController = ANCController(
        drag_body=drag_body,
        observer=observer,
        arm_actuator=arm_actuator,
        resettable=resettable,
        live_body=live_body,
        hz=args.hz,
        writer=dataset_writer,
        obs_spec=obs_spec,
        action_spec=get_simple_action_spec()
    )
    ui: ANCConsoleUI = ANCConsoleUI(controller)
    ui.start()
