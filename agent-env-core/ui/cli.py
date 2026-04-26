import threading
import asyncio
import json
import os

from controller.commands import *
from controller.controller import IANCController, ICommand
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from core.interfaces import IAnnotator



class ANCConsoleUI(IAnnotator):
    def __init__(self, anc_controller: IANCController, set_annotator: bool=False) -> None:
        self.anc_controller: IANCController = anc_controller
        if set_annotator is True: self.anc_controller.set_annotator(self)
        self.terminate_event: threading.Event = threading.Event()
        
        self.controller_thread = threading.Thread(target = self.anc_controller.run_loop, args = (self.terminate_event,), daemon=True)
        
        self.argless_command_mapping: dict[str, ICommand] = {
            "exit": ExitCommand(self.controller_thread, self.terminate_event),
            "stop": StopCommand(anc_controller),
            "drag": StartDragRecordCommand(anc_controller),
            "replay": ReplayRecordCommand(anc_controller),
            "go": GripperOpenCommand(anc_controller),
            "gc": GripperClosedCommand(anc_controller),
            "ref": TakeRefCommand(anc_controller),
            "inference": StartInferenceCommand(anc_controller),
        }
        self.help_command = ListCommandsCommand(self.argless_command_mapping)
        self.argless_command_mapping["help"] = self.help_command

        # For async cross-thread communication
        self.main_loop: asyncio.AbstractEventLoop | None = None
        self.prompt_task: asyncio.Task | None = None
        self.annotation_complete_event = threading.Event()
        self.annotation_result = {}
        self.session = PromptSession()
        # self.last_annotated_task_description: str = ""

        self.cache_file = ".annotation_cache.json"
        self.annotation_fields = ["task", "location", "camera_pos", "distractors", "blue_pos", "block_proximity"]
        self.cached_defaults = self._load_cache()

    def start(self):
        self.controller_thread.start()
        
        try:
            asyncio.run(self._async_start())
        except KeyboardInterrupt:
            self.terminate_event.set()
            self.controller_thread.join()
            exit(0)

    def _load_cache(self) -> dict:
        """Loads cached defaults from a JSON file, or creates empty ones."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass # Fallback to empty if file is corrupted
        
        # Return empty strings for all defined fields if no cache exists
        return {field: "" for field in self.annotation_fields}

    def _save_cache(self, current_annotations: dict):
        """Saves the accepted annotations to the JSON file for next time."""
        with open(self.cache_file, 'w') as f:
            json.dump(current_annotations, f, indent=4)

    async def _async_start(self):
        self.main_loop = asyncio.get_running_loop()
        
        with patch_stdout():
            while True:
                try:
                    self.prompt_task = asyncio.create_task(self.session.prompt_async("agent-env-core> "))
                    prompt_input = await self.prompt_task
                    
                    if not prompt_input:
                        continue
                        
                    prompt_input: str = prompt_input.strip().lower()
                    if prompt_input.count(" ") == 0: # If no spaces, we assume argless
                        command: ICommand | None = self.argless_command_mapping.get(prompt_input)
                        if command:
                            command.execute()
                        else:
                            self.help_command.execute()
                    elif prompt_input.count(" ") > 0:
                        if prompt_input.split(" ")[0] == "instruct":
                            instruction = prompt_input.split(" ", 1)[1]
                            SetInstructionCommand(self.anc_controller, instruction).execute()


                        
                except asyncio.CancelledError:
                    if self.anc_controller.get_annotator():
                        # Triggers when main prompting is cancelled, assumes annotation is required... 
                        await self._run_annotation_prompts()

    async def _run_annotation_prompts(self):
        """Runs the annotation UI, awaited in the main loop."""
        print("Initiated annotation")
        
        while True:
            while True:
                success_input = await self.session.prompt_async("1. Is the recording successful? (y/n): ")
                success_input = success_input.strip().lower()
                if success_input in ('y', 'n'):
                    is_valid = (success_input == 'y')
                    break
                print("Error: Input must be 'y' or 'n'.")

            # --- NEW: Dynamic prompting for all fields ---
            current_annotations = {}
            for i, field in enumerate(self.annotation_fields, start=2):
                # Grab the cached value, default to empty string if not found
                cached_val = self.cached_defaults.get(field, "")
                
                # Prompt the user. If they just press Enter, it uses the cached_val
                prompt_str = f"{i}. {field.replace('_', ' ').capitalize()}: "
                val = await self.session.prompt_async(prompt_str, default=cached_val)
                current_annotations[field] = val.strip()

            # --- NEW: Dynamic Summary ---
            print("\n--- Summary ---")
            print(f"is_valid    : {is_valid}")
            for field, val in current_annotations.items():
                # Just formatting nicely to align the colons
                print(f"{field:<11} : {val}")

            while True:
                verify_input = await self.session.prompt_async("Are these answers correct? (y/n): ")
                verify_input = verify_input.strip().lower()
                if verify_input in ('y', 'n'):
                    break
                print("Error: Input must be 'y' or 'n'.")

            if verify_input == 'y':
                # --- NEW: Save to cache and prepare result ---
                self.cached_defaults.update(current_annotations)
                self._save_cache(self.cached_defaults)
                
                self.annotation_result = {"is_valid": is_valid}
                self.annotation_result.update(current_annotations)
                break

            print("\nRestarting annotation...\n")
        
        # Signal the controller thread that annotation is done
        self.annotation_complete_event.set()

    def get_annotation(self) -> dict:
        """Called by the background controller thread."""
        self.annotation_complete_event.clear()
        print("Annotate cleared") 
        # Tell the main thread's event loop to cancel the waiting prompt task
        if self.main_loop and self.prompt_task:
            self.main_loop.call_soon_threadsafe(self.prompt_task.cancel)
            # print("Main loop prompot canceled") 
        
        # Block the background thread until main thread completes annotation
        self.annotation_complete_event.wait()

        print("Complete event wait") 
        
        return self.annotation_result

