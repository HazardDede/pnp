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
            return round(random.uniform(1, 100), 2), round(random.uniform(8, 36), 2)
            # return None, None


class DHT(Polling):
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
        except:
            self.logger.error("Adafruit_DHT package is not available - Using dummy implementation")
            Adafruit_DHT = Adafruit_Dummy.Adafruit_DHT

        device_map = {'dht11': Adafruit_DHT.DHT11, 'dht22': Adafruit_DHT.DHT22, 'am2302': Adafruit_DHT.AM2302}
        humidity, temperature = Adafruit_DHT.read_retry(device_map[self.device], self.data_gpio)

        if humidity is None or temperature is None:
            raise PollingError("Failed to get '{}' @ GPIO {} readings...".format(self.device, str(self.data_gpio)))

        return {'humidity': round(float(humidity), 2), 'temperature': round(float(temperature), 2)}
