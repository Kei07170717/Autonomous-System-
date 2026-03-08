from core.interfaces import IObserver, ISensor


class Observer(IObserver):
    def __init__(self, sensors: list[ISensor]):
        self.sensors: list[ISensor] = sensors

    def get_observation(self):
        sensor_states = dict(
            map(lambda sensor:
                (sensor.get_id(), sensor.get_data()),
                self.sensors)
        )

        return {
            "Sensor_states": sensor_states,
        }
