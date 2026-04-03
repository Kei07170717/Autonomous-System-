from core.interfaces import IBody, IJointAnglesSensor, IArmActuator, IGripperActuator
from core.types import Action

class Body(IBody):
    def __init__(self, arm_sensor: IJointAnglesSensor, arm_actuator: IArmActuator, gripper_actuator: IGripperActuator):
        self.arm_sensor: IJointAnglesSensor = arm_sensor
        self.arm_actuator: IArmActuator = arm_actuator
        self.gripper_actuator: IGripperActuator = gripper_actuator

    
    # Shouldn't we normalize this action actually? If we assume certain dimensions, 
    # we might have trouble switching to different robot arms
    def affect_world(self, action: dict):
        # print(action)
        self.arm_actuator.set_joint_angles(action["arm_angles"])
        self.gripper_actuator.set_gripper_value(action["gripper"])
