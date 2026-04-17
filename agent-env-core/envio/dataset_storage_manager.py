import datetime
import os
import time
from abc import ABC, abstractmethod
from os import path


class IDatasetStorageManager(ABC):
    @abstractmethod
    def create_new_dataset_directory(self) -> str:
        pass

    @abstractmethod 
    def get_new_episode_path(self, dataset_dir: str, episode_index: int, suffix: str) -> str:
        pass


_DEFAULT_PATH = r"../local-datasets"
class DatasetStorageManager(IDatasetStorageManager):
    def __init__(self, dataset_root_dir: str = _DEFAULT_PATH) -> None:
        self.dataset_root_dir: str = dataset_root_dir

        if dataset_root_dir == _DEFAULT_PATH and not path.isdir(_DEFAULT_PATH):
            print("Creating new default dataset root directory at: ", path.abspath(_DEFAULT_PATH))
            os.mkdir(_DEFAULT_PATH)

        self._validate_root()

        # self.path_for_new_dataset

    def create_new_dataset_directory(self) -> str:
        """Creates and returns a path to an empty directory for the
        dataset to be build."""
        new_dataset_dir = self._generate_new_dataset_directory_path()

        if not path.isdir(new_dataset_dir) and not path.isfile(new_dataset_dir):
            os.mkdir(new_dataset_dir)
            print("Generated new dataset directory at: ", path.abspath(new_dataset_dir))
            return new_dataset_dir
        else:
            raise ValueError(
                "Generated dataset dir at " + str(new_dataset_dir) + " already exists"
            )

    def _validate_root(self):
        if not path.isdir(self.dataset_root_dir):
            raise FileNotFoundError("Could not locate dataset root dir: {}".format(self.dataset_root_dir))

        # if not path.

    def _generate_new_dataset_directory_path(self) -> str:
        # Format: YYYYMMDD_HHMMSS (e.g., 20260318_165639)
        suffix = "_" + time.strftime("%Y%m%d_%H%M%S")
        target_directory = path.join(self.dataset_root_dir, "run" + suffix)
        return target_directory

    def get_new_episode_path(self, dataset_dir: str, episode_index: int, suffix: str) -> str:
        """Returns a path like: ../local-datasets/run_20260401_161230/episode_0000 + suffix"""
        return path.join(dataset_dir, f"episode_{episode_index:04d}{suffix}")

