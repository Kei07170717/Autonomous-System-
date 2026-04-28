from core.interfaces import GripperSensorModule, IObserver, JointAnglesSensorModule, SensorModule
from util.utils import time_it


class Observer(IObserver):
    def __init__(self, sensors: list[SensorModule], instruction: str="place the red block on the green block"):
        self.sensors: list[SensorModule] = sensors
        self.instruction = instruction

    def get_observation(self):
        sensor_states = dict(
            map(lambda sensor:
                (sensor.get_id(), sensor.get_data()),
                self.sensors)
        )

        return sensor_states

    def attach_sensor_module(self, module: SensorModule):
        self.sensors.append(module)
    
    def set_instruction(self, instruction: str):
        self.instruction = instruction
        print(f"Instruction set to \"{self.instruction}\"")

    def get_instruction(self) -> str:
        return self.instruction

class OptimizedCobotObserver(IObserver):
    """
    An optimized observer that guarantees strict execution order.
    Hardware-critical serial reads (Joints, Gripper) are clustered at the 
    front of the queue to prevent serial bus timeouts caused by slow sensors.
    """
    def __init__(self, sensors: list[SensorModule], instruction: str="put the red block on top of the blue block"):
        self.cobot_sensors: list[SensorModule] = []
        self.other_sensors: list[SensorModule] = []
        self.instruction = instruction
        
        # Sort initial sensors
        for sensor in sensors:
            self.attach_sensor_module(sensor)
    
    @time_it
    def get_observation(self) -> dict:
        observation = {}
        
            
        for sensor in self.other_sensors:
            observation[sensor.get_id()] = sensor.get_data()
        
        for sensor in self.cobot_sensors:
            observation[sensor.get_id()] = sensor.get_data()
            
        return observation

    def attach_sensor_module(self, module: SensorModule):
        # Route sensors to the correct execution queue based on their type
        if isinstance(module, (JointAnglesSensorModule, GripperSensorModule)):
            self.cobot_sensors.append(module)
        else:
            self.other_sensors.append(module)
    
    def set_instruction(self, instruction: str):
        self.instruction = instruction
        print(f"Instruction set to \"{self.instruction}\"")

    def get_instruction(self) -> str:
        return self.instruction
