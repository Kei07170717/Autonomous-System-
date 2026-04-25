from core.interfaces import IBody, IJointAnglesSensor, IArmActuator, IGripperActuator
from core.types import Action
import time

class Body(IBody):
    def __init__(self, arm_sensor: IJointAnglesSensor, arm_actuator: IArmActuator, gripper_actuator: IGripperActuator):
        self.arm_sensor: IJointAnglesSensor = arm_sensor
        self.arm_actuator: IArmActuator = arm_actuator
        self.gripper_actuator: IGripperActuator = gripper_actuator

    
    # Shouldn't we normalize this action actually? If we assume certain dimensions, 
    # we might have trouble switching to different robot arms
    def affect_world(self, action: dict):
        # print(action)
        # print(f"-- affect-start: {__import__('datetime').datetime.now().microsecond // 1000} ms")
        self.arm_actuator.set_joint_angles(action["arm_angles"])
        self.gripper_actuator.set_gripper_state(action["gripper"])

        # print(f"-- affect-end: {__import__('datetime').datetime.now().microsecond // 1000} ms")

    def set_gripper_open(self):
        print("Opening gripper")
        return self.gripper_actuator.set_gripper_open()
    
    def set_gripper_closed(self):
        print("Closing Gripper")
        return self.gripper_actuator.set_gripper_closed()
