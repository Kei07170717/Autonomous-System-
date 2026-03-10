from core.interfaces import IArmActuator, IGripperActuator 

class DummyComponent(IArmActuator, IGripperActuator):

    def set_joint_angles(self, arm_pos: list[float]):
        pass

    def set_gripper_closed(self) -> None:
        pass

    def set_gripper_open(self) -> None:
        pass

    def set_gripper_value(self, value) -> None:
        pass
