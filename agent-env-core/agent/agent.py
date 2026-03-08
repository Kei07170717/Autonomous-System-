from environment import Action
from core.interfaces import Agent


class KinestheticAgent(Agent):
    '''This agent is passive, the actions it sends are mirrored from
    the observation. This agent is used for gathering 'drag&record' data,
    which can later be replayed through another agent. The environment should
    not exectute actions using this agent (observe_only mode).'''

    def get_action(obs: dict) -> Action:
        # TODO: return observed angles
        return Action([0, 0, 0, 0, 0, 0])
