from __future__ import annotations
from agent import RotatingAgent
from agent.agent import MediatorAgent
from controller.utils import disabled_in_this_state, print_action, print_observation
from remote.http_connection_service import HTTPRemoteActionProvider
from ..base_state import State
from . import reset
from core.interfaces import Agent
from environment import Environment
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..controller import ANCController

class InferenceState(State):
    """
    """
  
    def __init__(self, context: ANCController, verbose_mode: bool = True):
        super().__init__(context, state_name="Inference", color = ("White", 255, 255, 255 )) 
        
        self.agent: Agent = MediatorAgent(HTTPRemoteActionProvider("http://localhost:8777/act"))
        self.verbose_mode = verbose_mode
        

    def on_state_enter(self):
        super().on_state_enter()

        assert self.context.live_body is not None
        self.environment = Environment(self.context.observer, self.context.live_body, obs_spec=self.context.obs_spec, action_spec=self.context.action_spec)
        
        self.timestep = self.environment.reset()
        


    def on_state_exit(self):
        # Clean up...
        if self.environment is not None:
            self.environment.close()

    def execute(self):
        assert self.timestep is not None
        assert self.environment is not None

        action = self.agent.get_action(self.timestep.observation)
        if self.verbose_mode: print_action(action)
        self.timestep = self.environment.step(action)
        if self.verbose_mode: print_observation(self.timestep.observation)

        if self.timestep.last():
            self.context.set_state(reset.ResettingState(self.context))
    
    @disabled_in_this_state
    def open_gripper(self):
        pass
    
    @disabled_in_this_state
    def close_gripper(self):
        pass

    @disabled_in_this_state
    def start_replay_record(self):
        pass

    @disabled_in_this_state
    def start_drag_record(self):
        pass

    def stop(self):
        self.context.set_state(reset.ResettingState(self.context))

    @disabled_in_this_state
    def take_ref_image(self):
        pass

    @disabled_in_this_state
    def start_inference(self):
        pass
