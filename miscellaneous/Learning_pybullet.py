import pybullet as p
import time
import pybullet_data

#built in Physics server: GUI for graphical, and DIRECT fro non-graphical
physicsClient = p.connect(p.GUI)
#probably for training use DIRECT
#physicsClient = p.connect(p.DIRECT)

#using data from pybullet
p.setAdditionalSearchPath(pybullet_data.getDataPath())

#will let us know if connected to the physics Client
p.getConnectionInfo(physicsClient) 

"""
Loading file URDF, SDF, MJCF
"""
floorID = p.loadURDF("plane.urdf", basePosition = [0,0,0])
#humanoidID = p.loadURDF("table/table.urdf", basePosition = [0,0,0.2])
mycobot = p.loadURDF("mycobot_280jn_mujoco.urdf", basePosition = [0,0,0.01])

#gravity on (xaxis, yaxis, zaxis)
p.setGravity(0, 0, -9.81)

p.resetDebugVisualizerCamera(
    cameraDistance=0.8,      # smaller = closer
    cameraYaw=50,            # left-right angle
    cameraPitch=-30,         # up-down angle
    cameraTargetPosition=[0,0,0]  # point camera looks at
)

#disconnect from the server
#p.disconnect()


"""
#stepSimulation takes the action inside the simulation, on default 240Hz (number of discrete move per second)
while True:
    p.stepSimulation()
    time.sleep(1./240.) #wait for IRL clock to catch up after every single tiny move

#get current position and orientation of the base, expressed in quaternion [x,y,z,w], must specify the id of object
#p.getBasePositionAndOrientation(objectUniqueID = int)


#Orientation:
#Quanternion allows to represent orientation from 4D space. 

#p.getQuanternionFromEuler(eulerAngle = [X,Y,Z])

maxForce = 500
p.setJointMotorControl2(bodyUniqueId=objUid, 
jointIndex=0, 
controlMode=p.VELOCITY_CONTROL,
targetVelocity = targetVel,
force = maxForce)
"""
time.sleep(2) # Wait a bit so you can see the result

while True:
    p.stepSimulation()
    time.sleep(1./240.)


#learning pybullet

import pybullet as p
import time
import pybullet_data

#built in Physics server: GUI for graphical, and DIRECT fro non-graphical
physicsClient = p.connect(p.GUI)
#probably for training use DIRECT
#physicsClient = p.connect(p.DIRECT)

#using data from pybullet
p.setAdditionalSearchPath(pybullet_data.getDataPath())

#will let us know if connected to the physics Client
p.getConnectionInfo(physicsClient) 

"""
Loading file URDF, SDF, MJCF
"""
floorID = p.loadURDF("plane.urdf", basePosition = [0,0,0])
#humanoidID = p.loadURDF("table/table.urdf", basePosition = [0,0,0.2])
mycobot = p.loadURDF("mycobot_280jn_mujoco.urdf", basePosition = [0,0,0.01])

#gravity on (xaxis, yaxis, zaxis)
p.setGravity(0, 0, -9.81)

p.resetDebugVisualizerCamera(
    cameraDistance=0.8,      # smaller = closer
    cameraYaw=50,            # left-right angle
    cameraPitch=-30,         # up-down angle
    cameraTargetPosition=[0,0,0]  # point camera looks at
)

#disconnect from the server
#p.disconnect()


"""
#stepSimulation takes the action inside the simulation, on default 240Hz (number of discrete move per second)
while True:
    p.stepSimulation()
    time.sleep(1./240.) #wait for IRL clock to catch up after every single tiny move

#get current position and orientation of the base, expressed in quaternion [x,y,z,w], must specify the id of object
#p.getBasePositionAndOrientation(objectUniqueID = int)


#Orientation:
#Quanternion allows to represent orientation from 4D space. 

#p.getQuanternionFromEuler(eulerAngle = [X,Y,Z])

maxForce = 500
p.setJointMotorControl2(bodyUniqueId=objUid, 
jointIndex=0, 
controlMode=p.VELOCITY_CONTROL,
targetVelocity = targetVel,
force = maxForce)
"""
time.sleep(2) # Wait a bit so you can see the result

while True:
    p.stepSimulation()
    time.sleep(1./240.)
