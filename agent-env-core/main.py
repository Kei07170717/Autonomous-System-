import argparse
from config import MyCobot280PIObserverBuilder, SemiDummyObserverBuilder
from pathlib import Path
from controller import ANCController
from controller.ghost_image_service import GhostImageServer, IGhostImageServer
from core.interfaces import (
    BaseWriter,
    IArmActuator,
    IBody,
    IGripperActuator,
    IJointAnglesSensor,
    IResettable,
    IGripperSensor,
    IColorChanger
)
from core.types import SpecTree, TensorSpec
from envio.dataset_storage_manager import DatasetStorageManager, IDatasetStorageManager
from envio.writing import DummyWriter, HDF5Writer
from environment import Body, Observer
from hardware.camera import Camera
from hardware.dummy_components import DummyComponent
from hardware.my_cobot_280pi_adapter import MyCobot280PiAdapter
from remote.http_connection_service import HTTPRemoteActionProvider
from remote.interfaces import IRemoteActionProvider
from ui import ANCConsoleUI
import numpy as np


def get_simple_action_spec() -> SpecTree:
    return {
        "arm_angles": TensorSpec(shape=(6,), dtype=np.float32),
        "gripper": TensorSpec(shape=(), dtype=np.uint8),
    }


# def setup_and_parse_arguments()
def create_writer(
    writer_type: str,
    obs_spec: SpecTree,
    is_annotation_enabled: bool,
    dataset_storage_manager: IDatasetStorageManager,
) -> BaseWriter | None:
    obs_spec = obs_spec
    action_spec = get_simple_action_spec()
    if writer_type == "hdf5":
        return HDF5Writer(
            obs_spec, action_spec, is_annotation_enabled, dataset_storage_manager
        )
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

    parser.add_argument(
        "--live",
        action="store_true",
        help="If set, will try to connect to the arm, will crash if not connected.",
    )

    parser.add_argument(
        "--hz",
        type=int,
        default=10,  # Can definitely get this higher if we spend time optimizing the controlloop
        help="Hz that the controller will operate on; 10hz is 10 send_angles a second.",
    )

    parser.add_argument(
        "--external-cam-id",
        type=str,
        default="HD Pro Webcam C920",
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
        help="Type of writer for the recording replay.",
    )

    parser.add_argument(
        "--annotate",
        action="store_true",
        help="If set, will not prompt for annotation after replay",
    )
    
    parser.add_argument(
        "--ghost-ref",
        action="store_true",
        help="If set, allows creation of reference image for item alignment during demos. Launches image overlay on port 5000 during IdlingState. Helps with, e.g., placing blocks on their original position before launching replay.",
    )
    
    parser.add_argument(
        "--remote-act-url",
        type=str,
        default="http://127.0.0.1:8777/act",
        help="HTTP REST API endpoint that returns actions",
    )

    parser.add_argument(
        "--vla-preprocess",
        action="store_true",
        help="If set, will resize, center crop and convert from BGR to RGB.",
    )
    
    parser.add_argument(
        "--dataset-root-dir",
        type=str,
        default=str(Path(r"..").joinpath("local-datasets")),
        help="Path to the root of the dataset directory, will create a run directory in here."
    )

    args = parser.parse_args()

    # Initialize dummy components to pretend we have an arm
    dummy_component: DummyComponent = DummyComponent()
    arm_sensor: IJointAnglesSensor = dummy_component
    arm_actuator: IArmActuator = dummy_component
    gripper_actuator: IGripperActuator = dummy_component
    gripper_sensor: IGripperSensor = dummy_component
    resettable: IResettable = dummy_component
    color_changer: IColorChanger = dummy_component
    

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
        color_changer = cobot_adapter

    observer_builder.register_joint_angles_sensor()
    observer_builder.register_gripper_sensor_module()
    external_cam = observer_builder.build_and_register_camera_module("cam_external", args.external_cam_id, vla_preprocess=args.vla_preprocess)
    observer_builder.build_and_register_camera_module("cam_wrist", args.wrist_cam_id,
                                                      vla_preprocess=args.vla_preprocess, rotate_90deg_left=True)
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

    # Util for demonstrations
    ghost_image_server: IGhostImageServer | None = None
    if external_cam is not None and args.ghost_ref is True: 
         ghost_image_server = GhostImageServer(external_cam)

    # File IO to save recordings
    dataset_storage_manager: IDatasetStorageManager = DatasetStorageManager(args.dataset_root_dir)
    dataset_writer: BaseWriter | None = create_writer(
        args.writer, obs_spec, args.annotate, dataset_storage_manager
    )

    remote_action_provider: IRemoteActionProvider = HTTPRemoteActionProvider(args.remote_act_url)

    # Build the controller
    controller: ANCController = ANCController(
        drag_body=drag_body,
        observer=observer,
        arm_actuator=arm_actuator,
        resettable=resettable,
        live_body=live_body,
        hz=args.hz,
        writer=dataset_writer,
        color_changer = color_changer,
        obs_spec=obs_spec,
        action_spec=get_simple_action_spec(),
        ghost_image_server=ghost_image_server,
        remote_action_provider=remote_action_provider
    )

    # We wrap the controller with a simple CLI as UI
    ui: ANCConsoleUI = ANCConsoleUI(controller, set_annotator=args.annotate)
    ui.start()
