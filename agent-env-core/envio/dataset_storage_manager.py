import datetime
import os
import time
from abc import ABC, abstractmethod
from os import path


class IDatasetStorageManager(ABC):
    @abstractmethod
    def create_new_dataset_directory(self) -> str:
        pass


class DatasetStorageManager(IDatasetStorageManager):
    def __init__(self, dataset_root_dir: str = "/tmp/a") -> None:
        self.dataset_root_dir: str = dataset_root_dir
        self._validate_root()
        # self.path_for_new_dataset

    def create_new_dataset_directory(self) -> str:
        """Creates and returns a path to an empty directory for the
        dataset to be build."""
        new_dataset_dir = self._generate_new_dataset_directory_path()

        if not path.isdir(new_dataset_dir) and not path.isfile(new_dataset_dir):
            os.mkdir(new_dataset_dir)
            print("Generated new dataset directory at: ", new_dataset_dir)
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
        suffix = "_" + time.strftime("%d%b%Y-%H%M%S")
        target_directory = path.join(self.dataset_root_dir, "run" + suffix)
        return target_directory
