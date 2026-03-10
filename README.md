# Autonomous Systems Assignment

## agent-env-core

agent-env-core (anc) allows for custom Agents (different policy types) to interact with the Environment through a Body. Certain levels of abstraction is accounted for, making it possible to simply swap out the Agent for a different one using another Policy. A Body is composed of multiple actuators, which can be even swapped out for virtual ones.

### Running ANC

To run the code, make sure to build the python environment. First navigate to agent-env-core directory and run the following conda commands:

`conda env create -f environment.yml`

Followed by:

`conda activate anc`
