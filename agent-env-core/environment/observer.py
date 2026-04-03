from core.interfaces import IObserver, SensorModule


class Observer(IObserver):
    def __init__(self, sensors: list[SensorModule]):
        self.sensors: list[SensorModule] = sensors

    def get_observation(self):
        print(f"-- obs-start: {__import__('datetime').datetime.now().microsecond // 1000} ms")
        sensor_states = dict(
            map(lambda sensor:
                (sensor.get_id(), sensor.get_data()),
                self.sensors)
        )
        print(f"-- obs-end: {__import__('datetime').datetime.now().microsecond // 1000} ms")

        return sensor_states

    def attach_sensor_module(self, module: SensorModule):
        self.sensors.append(module)
