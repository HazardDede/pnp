import random
from datetime import datetime

import requests

from . import Polling, PollingError
from ...utils import safe_get, auto_str_ignore
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


@auto_str_ignore(ignore_list=["api_key"])
class OpenWeather(Polling):
    """
    Periodically polls weather data from the OpenWeatherMap api.

    Args:
        api_key (str): The api_key you got from OpenWeatherMap after registration.
        lat (float): Latitude. If you pass `lat`, you have to pass `lon` as well.
        lon (float): Longitude. If you pass `lon`, you have to pass `lat` as well.
        city_name (str): The name of your city. To minimize ambiguity use lat/lon or your country as a suffix,
            e.g. London,GB. You have to pass whether `city_name` or `lat/lon`.
        units (str on of (metric, imperial, kelvin)): Specify units for temperature and speed.
            imperial = fahrenheit + miles/hour, metric = celsius + m/secs, kelvin = kelvin + m/secs. Default is metric.
        tz (str, optional): Time zone to use for current time and last updated time. Default is your local timezone.

    Results:
        A dictionary containing the results from OpenWeatherMap. See the docs for more information.
    """
    __prefix__ = 'openweather'

    def __init__(self, api_key, lat=None, lon=None, city_name=None, units="metric", tz=None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.lat = Validator.cast_or_none(float, lat)
        self.lon = Validator.cast_or_none(float, lon)
        self.city_name = Validator.cast_or_none(str, city_name)
        if self.city_name is None and not self._validate_lat_lon():
            raise ValueError("You have to pass city_name or lat and lon.")

        Validator.one_of(["metric", "imperial", "kelvin"], units=units)
        self.units = units
        self.tz = Validator.cast_or_none(str, tz)

        from pytz import timezone
        from tzlocal import get_localzone
        self._tz = get_localzone() if self.tz is None else timezone(self.tz)

    def poll(self):
        url = self._create_request_url()
        resp = requests.get(url)
        if 200 != resp.status_code:
            raise PollingError("GET of '{url}' failed with status code = '{resp.status_code}'".format(**locals()))

        raw_data = resp.json()

        return dict(
            temperature=safe_get(raw_data, "main", "temp"),
            pressure=safe_get(raw_data, "main", "pressure"),
            humidity=safe_get(raw_data, "main", "humidity"),
            cloudiness=safe_get(raw_data, "clouds", "all"),
            wind=safe_get(raw_data, "wind"),
            poll_dts=datetime.now(self._tz).isoformat(),
            last_updated_dts=datetime.fromtimestamp(safe_get(raw_data, "dt"), tz=self._tz).isoformat(),
            raw=raw_data
        )

    def _validate_lat_lon(self):
        return self.lat is not None and self.lon is not None

    def _create_request_url(self):
        url = ("http://api.openweathermap.org/data/2.5/weather?"
               "units={self.units}&"
               "APPID={self.api_key}")
        if self.lat is None and self.lon is None:
            url += "&q={self.city_name}"
        else:
            url += "&lat={self.lat}&lon={self.lon}"
        return url.format(**locals())
