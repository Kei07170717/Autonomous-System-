from core.interfaces import IObserver, SensorModule


class Observer(IObserver):
    def __init__(self, sensors: list[SensorModule]):
        self.sensors: list[SensorModule] = sensors

    def get_observation(self):
        sensor_states = dict(
            map(lambda sensor:
                (sensor.get_id(), sensor.get_data()),
                self.sensors)
        )

        return {
            "Sensor_states": sensor_states,
        }
