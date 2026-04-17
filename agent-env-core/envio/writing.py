from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple
from dm_env import TimeStep
import numpy as np
import os
from core.interfaces import BaseWriter
from core.types import Action, TensorSpec

from envio.dataset_storage_manager import IDatasetStorageManager
import h5py
import os.path as path
import numpy as np
from abc import ABC, abstractmethod
import dm_env

#from dataset_storage_manager import DatasetStorageManager
import queue
import threading

class IActionSequenceWriter(ABC):
    def __init__(self, metadata: Optional[dict[str, Any]] = None) -> None:
        self.metadata = metadata

    @abstractmethod
    def write_metadata(self):
        pass

    @abstractmethod
    def write_episode(self, steps: list):
        pass

    # @abstractmethod
    # def write_step(self, action, observation):
    #     pass

    # @abstractmethod
    # def open(self):
    #     pass
    #
    # @abstractmethod
    # def close(self):
    #     pass


# _ACTION_INDEX_IN_STEP = 1 # bad, should be struct(?) (now it depends on Recorder)
class NumpyActionSequenceWriter(IActionSequenceWriter):
    def __init__(
        self, 
        write_path: str,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(metadata)
        self.write_path: str = write_path

    def write_metadata(self):
        pass

    def write_episode(self, steps: list[dict]):
        print("Writing with steps length: ", len(steps))
        # print("Step 0: ", steps[0])
        # print(type(steps[0][0]), type(steps[0][1])) 
        actions: list[list[float]] = [step["arm_angles"] for step in steps] # TODO: add gripper
        np.savetxt(self.write_path, np.asarray(actions), delimiter=",")


# class RLDSWriterAdapter(BaseWriter):
#     def __init__(self, obs_spec, action_spec, metadata=None) -> None:
#         super().__init__(obs_spec, action_spec, metadata)

class DummyWriter(BaseWriter):
    def __init__(self, obs_spec, action_spec, metadata=None) -> None:
        super().__init__(obs_spec, action_spec, metadata)
        print("Init writer with OBS SPEC: ", obs_spec)
        print("Init writer with ACTION SPEC: ", action_spec)

    def write_step(self, action, timestep ):
        print("Writing dummy step..")

    def prepare_new_episode(self, initial_timestep: TimeStep):
        print("Preparing dummy episode...")

    def close(self):
        print("Closing dummy writer...")



# Assuming TensorSpec and SpecTree are defined as before

class HDF5Writer(BaseWriter):
    def __init__(self, obs_spec, action_spec, is_annotation_enabled: bool, storage_manager: IDatasetStorageManager, buffer_size=8, compression: bool = False, metadata=None) -> None:
        super().__init__(obs_spec, action_spec, is_annotation_enabled, metadata)
        self.storage_manager = storage_manager
        self.buffer_size = buffer_size # TODO: chunk sizes should be kept under the h5 chunk cache (default 1mb)
        self.compression = compression # Performance impact needs to be researched/justified
        self.episode_index = 0
        self.current_file = None
        self.dataset_dir: str | None = None
        self.SUFFIX = ".hdf5"
        
        # 1. Flatten the SpecTrees into HDF5 paths dynamically
        self.flat_specs: dict = self._flatten_specs("observations", self.obs_spec)
        self.flat_specs.update(self._flatten_specs("actions", self.action_spec))
        
        # Add standard RLDS fields
        self.flat_specs.update({
            "rewards": TensorSpec(shape=(), dtype=np.float32),
            "discounts": TensorSpec(shape=(), dtype=np.float32),
            "is_first": TensorSpec(shape=(), dtype=bool),
            "is_last": TensorSpec(shape=(), dtype=bool),
            "is_terminal": TensorSpec(shape=(), dtype=bool),
        })
        
        self._clear_buffer()
        # Background writer state
        self._write_queue = queue.Queue(maxsize=8)#!
        self._stop_token = object()
        self._writer_thread = None

    def _flatten_specs(self, prefix: str, spec) -> dict:
        """Recursively parses a SpecTree into a flat dict of {hdf5_path: TensorSpec}"""
        paths: dict = {}
        if isinstance(spec, dict):
            for k, v in spec.items():
                paths.update(self._flatten_specs(f"{prefix}/{k}", v))
        else:
            paths[prefix] = spec
        return paths

    def _clear_buffer(self):
        """Initializes empty lists for every dynamic path."""
        self.buffer = {path: [] for path in self.flat_specs.keys()}

    def _calculate_optimal_chunk_shape(self, spec: TensorSpec, target_bytes=1_000_000) -> Tuple[int, int]:
        """
        Calculates a temporal chunk size for given spec.
        """
        np_dtype = np.dtype(spec.dtype)
        elements_per_step: int = int(np.prod(spec.shape)) if spec.shape else 1
        bytes_per_step: int = elements_per_step * np_dtype.itemsize
        
        if bytes_per_step == 0: 
            return (2, *spec.shape) # Fallback to minimal even chunk

        # Calculate raw steps to hit target bytes (default 1MB limit for Pi)
        raw_steps = int(target_bytes / bytes_per_step)
        
        # Force the temporal chunk to be at least 2, and cleanly divisible by 2
        temporal_chunk: int = max(2, raw_steps - (raw_steps % 2))
        
        # Cap to 256. This is less than your min episode length (300).
        # It prevents HDF5 from allocating massive empty chunks on disk for short episodes.
        temporal_chunk: int = min(temporal_chunk, 256) 
        
        return (temporal_chunk, *spec.shape)

    def _writer_loop(self):
        while True:
            item = self._write_queue.get()
            try:
                if item is self._stop_token:
                    return
                self._flush_batch(item)
            finally:
                self._write_queue.task_done()
    
    def prepare_new_episode(self, initial_timestep: dm_env.TimeStep):
        # Close previous episode if one was open
        self.close() 

        # Create dir if we didn't already
        if self.dataset_dir is None:
            self.dataset_dir = self.storage_manager.create_new_dataset_directory()

        # Open new HDF5 file
        filepath = self.storage_manager.get_new_episode_path(self.dataset_dir, self.episode_index, self.SUFFIX)
        self.current_file = h5py.File(filepath, 'w')
       
        # Dynamically create resizable chunked datasets
        for h5_path, spec in self.flat_specs.items():
            # dynamically calculate the chunk shape based on data size
            optimal_chunk_shape = self._calculate_optimal_chunk_shape(spec)

            self.current_file.create_dataset(
                name = h5_path,
                shape = (0, *spec.shape),        # Start empty
                maxshape = (None, *spec.shape),  # Allow infinite resizing on axis 0
                dtype = spec.dtype,
                # chunks=(self.chunk_size, *spec.shape) # Implicitly turned on when using compression
                chunks = optimal_chunk_shape
                ) # TODO: Consider if compression is justified
            
        self._clear_buffer()
        
        # Start writer thread for this episode
        self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._writer_thread.start()

        # Handle the initial step (generate dummy zeros for the action)
        dummy_action = self._generate_dummy_data(self.action_spec)
        self.write_step(dummy_action, initial_timestep)
        
        

    def _write_episode_metadata(self, metadata: dict):
        assert self.current_file is not None
        
        for key, value in metadata.items():
            self.current_file.attrs[key] = value

    def write_step(self, action, timestep: dm_env.TimeStep):
        # Extract observations and actions dynamically
        self._extract_to_buffer("observations", timestep.observation)
        self._extract_to_buffer("actions", action)
        
        # Extract RLDS standard fields
        self.buffer["rewards"].append(0.0 if timestep.reward is None else timestep.reward)
        self.buffer["discounts"].append(1.0 if timestep.discount is None else timestep.discount)
        self.buffer["is_first"].append(timestep.first())
        self.buffer["is_last"].append(timestep.last())
        self.buffer["is_terminal"].append(timestep.last() and timestep.discount == 0.0)

        # Flush if buffer reaches chunk limit
        if len(self.buffer["is_first"]) >= self.buffer_size:
            self._send_batch_to_queue()

    def _extract_to_buffer(self, prefix: str, data):
        """Recursively pulls data from nested dicts and appends to flat buffer."""
        if isinstance(data, dict):
            for k, v in data.items():
                self._extract_to_buffer(f"{prefix}/{k}", v)
        else:
            self.buffer[prefix].append(data)

    def _generate_dummy_data(self, spec):
        """Recursively generates zeros for the initial step's dummy action."""
        if isinstance(spec, dict):
            return {k: self._generate_dummy_data(v) for k, v in spec.items()}
        else:
            return np.zeros(spec.shape, dtype=spec.dtype)
    
    def _send_batch_to_queue(self):
        """Moves current RAM buffer into the write queue."""
        current_batch_size = len(self.buffer["is_first"])
        if current_batch_size == 0 or self.current_file is None:
            return

        batch = self.buffer
        self._clear_buffer()
        self._write_queue.put(batch)
    
    
    def _flush_batch(self, batch):
        """Resizes HDF5 datasets and writes the RAM buffer to disk."""
        current_batch_size = len(batch["is_first"])
        if current_batch_size == 0 or self.current_file is None:
            return

        for path, data_list in batch.items():
            dataset = self.current_file[path]
            assert isinstance(dataset, h5py.Dataset), f"Expected {path} to be a Dataset"

            current_len = dataset.shape[0]
            
            # Resize dataset to make room for new chunk # TODO: too much overhead?
            dataset.resize(current_len + current_batch_size, axis=0)
            
            # Write stacked chunk to disk
            dataset[current_len:] = np.stack(data_list)
            
   

    # def set_episode_end_callback(self, func):
    #     self.end_of_episode_callback = func

    def set_annotation(self, annotation: dict):
        """Write (task) annotation for last episode"""
        self.is_annotation_needed = False
        pass

    def close(self):
        """Flushes remaining buffer and cleanly closes the file."""

        if self.current_file is None:
            return

        annotation = {}
        if self.is_annotation_enabled and self.end_of_episode_annotation_callback:
            annotation: dict = self.end_of_episode_annotation_callback()
            self._write_episode_metadata(annotation)

        self._send_batch_to_queue()
        # Wait until all queued writes are finished
        self._write_queue.join()

        # Stop writer thread
        if self._writer_thread is not None:
            self._write_queue.put(self._stop_token)
            self._write_queue.join()
            self._writer_thread.join()
            self._writer_thread = None
        # Update file-level attributes right before closing
        rewards_dataset = self.current_file["rewards"]
        
        assert isinstance(rewards_dataset, h5py.Dataset), "Expected rewards to be a Dataset"
        self.current_file.attrs["episode_id"] = self.episode_index
        self.current_file.attrs["length"] = rewards_dataset.shape[0]
        self.current_file.attrs["total_reward"] = float(np.sum(rewards_dataset[:]))
        ep_path = self.current_file.filename
       

        self.current_file.close()
        if annotation.get("is_valid", True):
            print(f"Episode {self.episode_index} stored in: {ep_path}")
        else:
            os.remove(ep_path)    
            print(f"Removed episode because invalid")
        
        self.episode_index += 1
        self.current_file = None
