"""Useful sensor stuff."""

import logging
import os
from datetime import datetime, timedelta

import requests

from . import PullBase, Polling, PollingError
from .. import load_optional_module
from ...utils import safe_get, auto_str_ignore, parse_duration_literal, Throttle
from ...validator import Validator


class DHT(Polling):
    """
    Periodically polls a dht11 or dht22 (aka am2302) for temperature and humidity readings.
    Polling interval is controlled by `interval`.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/sensor.DHT/index.md
    """
    __prefix__ = 'dht'

    EXTRA = 'dht'

    def __init__(self, device='dht22', data_gpio=17, humidity_offset=0.0, temp_offset=0.0,
                 **kwargs):
        super().__init__(**kwargs)
        valid_devices = ['dht11', 'dht22', 'am2302']
        self.device = str(device).lower()
        Validator.one_of(valid_devices, device=self.device)
        self.data_gpio = int(data_gpio)
        self.humidity_offset = float(humidity_offset)
        self.temp_offset = float(temp_offset)

    @staticmethod
    def _load_dht_package():
        try:
            import Adafruit_DHT as Pkg
        except ImportError:  # pragma: no cover
            logger = logging.getLogger(__name__)
            logger.warning("Adafruit_DHT package is not available - Using mock")
            from ...mocking import DHTMock as Pkg
        return Pkg

    def poll(self):
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


@auto_str_ignore(['_poller'])
class MiFlora(Polling):
    """
    Periodically polls a xiaomi miflora plant sensor for sensor readings via btle.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/sensor.MiFlora/index.md

    """
    EXTRA = 'miflora'

    def __init__(self, mac, adapter='hci0', **kwargs):
        super().__init__(**kwargs)
        self.mac = str(mac)
        self.adapter = str(adapter)
        self._poller = None

    def _find_backend(self):
        try:
            import bluepy.btle  # noqa: F401 pylint: disable=unused-import
            from btlewrap import BluepyBackend
            backend = BluepyBackend
        except ImportError:
            from btlewrap import GatttoolBackend
            backend = GatttoolBackend
        self.logger.debug("Miflora for %s is using %s backend", self.mac, backend.__name__)
        return backend

    def _init(self):
        if self._poller:
            # We already got a miflora poller -> abort
            return

        mfp = load_optional_module('miflora.miflora_poller', self.EXTRA)
        self._poller = mfp.MiFloraPoller(
            mac=self.mac, adapter=self.adapter, backend=self._find_backend()
        )
        self.logger.debug("Initialization for %s finished", self.mac)

    def _connect_sensor(self):
        assert self._poller

        from btlewrap import BluetoothBackendException
        try:
            self.logger.debug("Reading miflora sensor: %s", self.mac)
            self._poller.fill_cache()
        except IOError as ioerr:
            raise PollingError() from ioerr
        except BluetoothBackendException as bterror:
            raise PollingError() from bterror

    def _get_sensor_readings(self):
        assert self._poller

        mfp = load_optional_module('miflora.miflora_poller', self.EXTRA)
        reading_params = [mfp.MI_CONDUCTIVITY, mfp.MI_LIGHT, mfp.MI_MOISTURE,
                          mfp.MI_TEMPERATURE, mfp.MI_BATTERY]
        res = {para: self._poller.parameter_value(para) for para in reading_params}
        return {**res, **{'firmware': self._poller.firmware_version()}}

    def poll(self):
        self._init()
        self._connect_sensor()
        readings = self._get_sensor_readings()
        self.logger.info("Miflora readings for '%s': %s", self.mac, readings)
        return readings


@auto_str_ignore(ignore_list=["api_key"])
class OpenWeather(Polling):
    """
    Periodically polls weather data from the OpenWeatherMap api.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/sensor.OpenWeather/index.md
    """
    __prefix__ = 'openweather'

    def __init__(self, api_key, lat=None, lon=None, city_name=None, units="metric", tz=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.lat = Validator.cast_or_none(float, lat)
        self.lon = Validator.cast_or_none(float, lon)
        self.city_name = Validator.cast_or_none(str, city_name)
        if self.city_name is None and not self._validate_lat_lon():
            raise ValueError("You have to pass city_name or lat and lon.")

        Validator.one_of(["metric", "imperial", "kelvin"], units=units)
        self.units = units
        self.tzone = Validator.cast_or_none(str, tz)

        from pytz import timezone
        from tzlocal import get_localzone
        self._tz = get_localzone() if self.tzone is None else timezone(self.tzone)

    def poll(self):
        url = self._create_request_url()
        resp = requests.get(url)
        if resp.status_code != 200:
            raise PollingError("GET of '{url}' failed with status "
                               "code = '{resp.status_code}'".format(**locals()))

        raw_data = resp.json()

        return dict(
            temperature=safe_get(raw_data, "main", "temp"),
            pressure=safe_get(raw_data, "main", "pressure"),
            humidity=safe_get(raw_data, "main", "humidity"),
            cloudiness=safe_get(raw_data, "clouds", "all"),
            wind=safe_get(raw_data, "wind"),
            poll_dts=datetime.now(self._tz).isoformat(),
            last_updated_dts=datetime.fromtimestamp(
                safe_get(raw_data, "dt"), tz=self._tz).isoformat(),
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


# pylint: disable=too-many-instance-attributes
@auto_str_ignore(ignore_list=['cool_down_secs', 'notify', 'signal_fft', 'signal_length'])
class Sound(PullBase):
    """
    Listens to the microphone in realtime and searches the stream for a specific sound pattern.
    Practical example: I use this plugin to recognize my doorbell without tampering with
    the electrical device ;-)

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/sensor.Sound/index.md
    """
    EXTRA = 'sound'

    MODE_PEARSON = 'pearson'
    MODE_STD = 'std'
    ALLOWED_MODES = [MODE_PEARSON, MODE_STD]
    RATE = 44100
    CHUNK_SIZE = 1024 * 4
    PEARSON_THRESHOLD = 0.5
    STD_THRESHOLD = 1.4

    def __init__(self, wav_file, device_index=None, mode='pearson', sensitivity_offset=0.0,
                 cool_down="10s", ignore_overflow=False, **kwargs):
        super().__init__(**kwargs)
        self.wav_file = str(wav_file)
        if not os.path.isabs(self.wav_file):
            self.wav_file = os.path.join(self.base_path, self.wav_file)
        Validator.is_file(wav_file=self.wav_file)
        self.device_index = device_index and int(device_index)
        self.wav_file_name = os.path.basename(os.path.splitext(self.wav_file)[0])
        self.signal_length, self.signal_fft = self._load_wav_fft()
        self.mode = str(mode)
        Validator.one_of(self.ALLOWED_MODES, mode=self.mode)
        self.sensitivity_offset = float(sensitivity_offset)
        self.cool_down = cool_down
        self.cool_down_secs = cool_down and parse_duration_literal(cool_down)  # Might be None
        self.ignore_overflow = bool(ignore_overflow)
        # Override notify with a throttled version
        self.notify = Throttle(timedelta(seconds=self.cool_down_secs or 0))(self.notify)

    def _load_wav_fft(self):
        wavfile = load_optional_module('scipy.io.wavfile', self.EXTRA)
        self.logger.debug("Loading wav file from '%s'", self.wav_file)
        sample_rate, signal = wavfile.read(self.wav_file)
        N, secs, signal_fft = self._perform_fft(signal, sample_rate)
        self.logger.debug("Loaded %s seconds wav file @ %s hz", secs, sample_rate)
        return N, signal_fft

    def _perform_fft(self, signal, rate, add_zeros=True):
        np = load_optional_module('numpy', self.EXTRA)
        scipy = load_optional_module('scipy', self.EXTRA)

        chn = len(signal.shape)
        if chn >= 2:  # Make mono channel
            signal = signal.sum(axis=1) / 2
        N = int(signal.shape[0])
        secs = N / float(rate)
        if add_zeros:
            signal = np.concatenate((signal, np.zeros(len(signal))), axis=None)
        trans_fft = abs(scipy.fft(signal))

        return N, secs, trans_fft

    def _similarity(self, buffer):
        _, _, current_fft = self._perform_fft(buffer[:self.signal_length], self.RATE, True)
        if self.mode == self.MODE_PEARSON:
            pearsonr = load_optional_module('scipy.stats.stats', self.EXTRA).pearsonr
            corrcoef = pearsonr(self.signal_fft, current_fft)[0]
            threshold = self.PEARSON_THRESHOLD + self.sensitivity_offset
        else:
            np = load_optional_module('numpy', self.EXTRA)
            corrcoef = np.correlate(
                self.signal_fft / self.signal_fft.std(),
                current_fft / current_fft.std()
            )[0] / len(self.signal_fft)
            threshold = self.STD_THRESHOLD + self.sensitivity_offset

        return corrcoef >= threshold, corrcoef, threshold

    def pull(self):
        np = load_optional_module('numpy', self.EXTRA)
        pyaudio = load_optional_module('pyaudio', self.EXTRA)

        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            input_device_index=self.device_index,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE
        )
        try:
            buffer = None
            N = self.signal_length
            while not self.stopped:
                data = np.fromstring(stream.read(
                    self.CHUNK_SIZE,
                    exception_on_overflow=self.ignore_overflow
                ), dtype=np.int16)
                buffer = data if buffer is None else np.concatenate((buffer, data), axis=None)
                lbuf = len(buffer)
                if lbuf >= N:
                    self.logger.debug("Buffer (%s) >= size of wav file (%s)",
                                      lbuf, N)
                    flag, corrcoef, threshold = self._similarity(buffer)
                    self.logger.debug("Correlation: %s >= %s = %s",
                                      corrcoef, threshold, flag)
                    if flag:
                        self.notify({
                            'data': self.wav_file_name,
                            'corrcoef': corrcoef,
                            'threshold': threshold
                        })
                        buffer = None
                    else:
                        buffer = buffer[int(len(buffer) * 0.75):]
        finally:
            stream.close()
            pa.terminate()
