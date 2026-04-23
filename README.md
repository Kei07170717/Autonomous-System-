# Autonomous Systems Assignment

## agent-env-core

agent-env-core (anc) allows for custom Agents (different policy types) to interact with the Environment through a Body. Certain levels of abstraction is accounted for, making it possible to simply swap out the Agent for a different one using another Policy. A Body is composed of multiple actuators, which can be even swapped out for virtual ones.

### Running ANC

To run the code, make sure to build the python environment. First navigate to agent-env-core directory and run the following conda commands:

`conda env create -f environment.yml`

Followed by:

`conda activate anc`

### Recording for Demonstrations

```bash
python main.py --live --external-cam-id='Elgato Facecam: Elgato Facecam' --wrist-cam-id='USB 2.0 Camera: USB 2.0 Camera' --annotate
```

### Remote Inference

#### A(PI) -> B <- C(GPU4EDU) API connection 
This approach runs the API on the GPU4EDU cluster with a middleman between the cluster and the PI that bridges the two ports.

##### On Device A (PI) 
```bash
ssh -N -L 8777:localhost:8888 mms@77.172.166.178 -p 42069
```
This tunnels the port of 8777 of the Cobot to port 8888 of the middleman


##### On Device C (Compute Node)

To start the API on the cluster, create an ssh session to the login node of the cluster and launch the inference job. 

Then enter the compute node the API is running on and run: 
```bash
ssh -N -R 8888:localhost:8777 mms@77.172.166.178 -p 42069
```
This reverse tunnels the port 8777 of the compute node to port 8888 of the middleman.

> [!NOTE]  
> To get to the compute node, first enter the login node:
> ```bash
> ssh unumber@aurometalsaurus.uvt.nl
> ```
> Then enter the compute node:
> ```bash
> srun --nodes=1 --nodelist=[nodename] --pty /bin/bash -l
> ```