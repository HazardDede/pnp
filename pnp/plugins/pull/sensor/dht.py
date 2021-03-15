"""Pull: sensor.DHT"""

import logging
import random
from typing import Any, Tuple

from pnp import validator
from pnp.plugins.pull import PollingError, SyncPolling
from pnp.typing import Payload


__EXTRA__ = 'dht'

Readings = Tuple[float, float]


class DHTMock:  # pragma: no cover
    """Mocks a DHT device (because the adafruit pkg is only available on rpi's)."""
    DHT22 = "dht22"
    DHT11 = "dht11"
    AM2302 = "am2302"

    @staticmethod
    def read_retry(sensor: str, pin: int) -> Readings:
        """Read the sensor values (humidity, temperature)."""
        _, _ = sensor, pin
        return (
            round(random.uniform(1, 100), 2),
            round(random.uniform(8, 36), 2)
        )


class DHT(SyncPolling):
    """
    Periodically polls a dht11 or dht22 (aka am2302) for temperature and humidity readings.
    Polling interval is controlled by `interval`.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#sensor-dht
    """
    __REPR_FIELDS__ = ['data_gpio', 'device', 'humidity_offset', 'temp_offset']

    def __init__(
            self, device: str = 'dht22', data_gpio: int = 17,
            humidity_offset: float = 0.0, temp_offset: float = 0.0, **kwargs: Any
    ):
        super().__init__(**kwargs)
        valid_devices = ['dht11', 'dht22', 'am2302']
        self.device = str(device).lower()
        validator.one_of(valid_devices, device=self.device)
        self.data_gpio = int(data_gpio)
        self.humidity_offset = float(humidity_offset)
        self.temp_offset = float(temp_offset)

    @staticmethod
    def _load_dht_package() -> Any:
        try:
            import Adafruit_DHT as Pkg
        except ImportError:  # pragma: no cover
            logger = logging.getLogger(__name__)
            logger.warning("Adafruit_DHT package is not available - Using mock")
            Pkg = DHTMock
        return Pkg

    def _poll(self) -> Payload:
        # Adafruit package is optional - import at the last moment
        pkg = self._load_dht_package()

        device_map = {'dht11': pkg.DHT11, 'dht22': pkg.DHT22, 'am2302': pkg.AM2302}
        humidity, temperature = pkg.read_retry(device_map[self.device], self.data_gpio)

        if humidity is None or temperature is None:
            raise PollingError("Failed to get '{}' @ GPIO {} readings...".format(
                self.device, str(self.data_gpio)))

        return {
            'humidity': round(float(humidity) + self.humidity_offset, 2),
            'temperature': round(float(temperature) + self.temp_offset, 2)
        }
