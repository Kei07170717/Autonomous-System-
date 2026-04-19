import threading
import asyncio

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
        
        self.command_mapping: dict[str, ICommand] = {
            "exit": ExitCommand(self.controller_thread, self.terminate_event),
            "stop": StopCommand(anc_controller),
            "drag": StartDragRecordCommand(anc_controller),
            "replay": ReplayRecordCommand(anc_controller),
            "go": GripperOpenCommand(anc_controller),
            "gc": GripperClosedCommand(anc_controller),
            "ref": TakeRefCommand(anc_controller),
            "inference": StartInferenceCommand(anc_controller)
        }
        self.help_command = ListCommandsCommand(self.command_mapping)
        self.command_mapping["help"] = self.help_command

        # For async cross-thread communication
        self.main_loop: asyncio.AbstractEventLoop | None = None
        self.prompt_task: asyncio.Task | None = None
        self.annotation_complete_event = threading.Event()
        self.annotation_result = {}
        self.session = PromptSession()
        self.last_annotated_task_description: str = ""

    def start(self):
        self.controller_thread.start()
        
        try:
            asyncio.run(self._async_start())
        except KeyboardInterrupt:
            self.terminate_event.set()
            self.controller_thread.join()
            exit(0)

    async def _async_start(self):
        self.main_loop = asyncio.get_running_loop()
        
        with patch_stdout():
            while True:
                try:
                    self.prompt_task = asyncio.create_task(self.session.prompt_async("agent-env-core> "))
                    prompt_input = await self.prompt_task
                    
                    if not prompt_input:
                        continue
                        
                    prompt_input = prompt_input.strip().lower()
                    command: ICommand | None = self.command_mapping.get(prompt_input)
                    if command:
                        command.execute()
                    else:
                        self.help_command.execute()
                        
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

            task = await self.session.prompt_async("2. Annotate task: ", default=self.last_annotated_task_description)
            task = task.strip()
            self.last_annotated_task_description = task

            print("\n--- Summary ---")
            print(f"is_valid : {is_valid}")
            print(f"task     : {task}")

            while True:
                verify_input = await self.session.prompt_async("Are these answers correct? (y/n): ")
                verify_input = verify_input.strip().lower()
                if verify_input in ('y', 'n'):
                    break
                print("Error: Input must be 'y' or 'n'.")

            if verify_input == 'y':
                self.annotation_result = {"is_valid": is_valid, "task": task}
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

