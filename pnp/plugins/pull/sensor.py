import random

from . import Polling, PollingError
from ...validator import Validator


class Adafruit_Dummy:
    class Adafruit_DHT:
        DHT22 = "dht22"
        DHT11 = "dht11"
        AM2302 = "am2302"

        @staticmethod
        def read_retry(sensor, pin):
            return round(random.uniform(1, 100), 2), round(random.uniform(8, 36), 2)  # pragma: no cover


class DHT(Polling):
    """
    Periodically polls a dht11 or dht22 (aka am2302) for temperature and humidity readings.
    Polling interval is controlled by `interval`.

    Args:
        device (str): The device to poll (one of dht22, dht11, am2302)
        data_gpio (int): The data gpio port where the device operates on.

    Returns:
        The callback `on_payload` passes a dictionary containing `temperature` and `humidity`.

    Example configuration:

    name: dht
        pull:
          plugin: pnp.plugins.pull.sensor.DHT
          args:
            device: dht22  # Connect to a dht22
            data_gpio: 17  # DHT is connected to gpio port 17
            interval: 5m  # Polls the readings every 5 minutes
        push:
          - plugin: pnp.plugins.push.simple.Echo
            selector: payload.temperature  # Temperature reading
          - plugin: pnp.plugins.push.simple.Echo
            selector: payload.humidity  # Humidity reading

    """
    __prefix__ = 'dht'

    def __init__(self, device='dht22', data_gpio=17, **kwargs):
        super().__init__(**kwargs)
        valid_devices = ['dht11', 'dht22', 'am2302']
        self.device = str(device).lower()
        Validator.one_of(valid_devices, device=self.device)
        self.data_gpio = int(data_gpio)

    def poll(self):
        # Adafruit package is optional - import at the last moment
        try:
            import Adafruit_DHT
        except:  # pragma: no cover
            self.logger.error("Adafruit_DHT package is not available - Using dummy implementation")
            Adafruit_DHT = Adafruit_Dummy.Adafruit_DHT

        device_map = {'dht11': Adafruit_DHT.DHT11, 'dht22': Adafruit_DHT.DHT22, 'am2302': Adafruit_DHT.AM2302}
        humidity, temperature = Adafruit_DHT.read_retry(device_map[self.device], self.data_gpio)

        if humidity is None or temperature is None:
            raise PollingError("Failed to get '{}' @ GPIO {} readings...".format(self.device, str(self.data_gpio)))

        return {'humidity': round(float(humidity), 2), 'temperature': round(float(temperature), 2)}
