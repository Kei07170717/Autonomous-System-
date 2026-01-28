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
R2D2ID = p.loadURDF("r2d2.urdf", basePosition = [0,0,0.5])

#disconnect from the server
#p.disconnect()

#gravity on (xaxis, yaxis, zaxis)
p.setGravity(0, 0, -9.81)

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

head_joint = 0
wheel_joints = [2, 3, 6, 7] # R2D2 has several wheel segments

# 2. COMMAND: Set the desired motion
# Turn head to 1.5 radians and roll wheels at velocity 5
p.setJointMotorControl2(R2D2ID, head_joint, p.POSITION_CONTROL, targetPosition=1.5)

for wheel in wheel_joints:
    p.setJointMotorControl2(R2D2ID, wheel, p.VELOCITY_CONTROL, targetVelocity=30)

# 3. EXECUTION: Run the loop for exactly 3 seconds (720 steps)
print("R2D2 is moving...")
for _ in range(720):
    p.stepSimulation()
    time.sleep(1./240.)

# 4. STOP: Set velocity back to zero
for wheel in wheel_joints:
    p.setJointMotorControl2(R2D2ID, wheel, p.VELOCITY_CONTROL, targetVelocity=0)

print("Movement finished.")
time.sleep(2) # Wait a bit so you can see the result
p.disconnect()
