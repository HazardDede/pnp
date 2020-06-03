"""Useful sensor stuff."""

import logging
from datetime import datetime
from functools import partial

import attr
import requests
import schema as sc

from pnp import validator
from pnp.plugins import load_optional_module
from pnp.plugins.pull import PullBase, Polling, PollingError
from pnp.shared.sound import (
    WavFile,
    similarity_pearson,
    similarity_std,
    MODE_PEARSON,
    MODE_STD,
    ALLOWED_MODES
)
from pnp.utils import (
    safe_get,
    auto_str_ignore,
    parse_duration_literal,
    Cooldown
)


class DHT(Polling):
    """
    Periodically polls a dht11 or dht22 (aka am2302) for temperature and humidity readings.
    Polling interval is controlled by `interval`.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/sensor.DHT/index.md
    """
    EXTRA = 'dht'

    def __init__(self, device='dht22', data_gpio=17, humidity_offset=0.0, temp_offset=0.0,
                 **kwargs):
        super().__init__(**kwargs)
        valid_devices = ['dht11', 'dht22', 'am2302']
        self.device = str(device).lower()
        validator.one_of(valid_devices, device=self.device)
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

    def __init__(self, api_key, lat=None, lon=None, city_name=None, units="metric", tz=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.lat = lat and float(lat)
        self.lon = lon and float(lon)
        self.city_name = city_name and str(city_name)
        if self.city_name is None and not self._validate_lat_lon():
            raise ValueError("You have to pass city_name or lat and lon.")

        validator.one_of(["metric", "imperial", "kelvin"], units=units)
        self.units = units
        self.tzone = tz and str(tz)

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
@auto_str_ignore(ignore_list=[])
class Sound(PullBase):
    """
    Listens to the microphone in realtime and searches the stream for a specific sound pattern.
    Practical example: I use this plugin to recognize my doorbell without tampering with
    the electrical device ;-)

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/sensor.Sound/index.md
    """
    @attr.s
    class WavConfig:
        """Wav configuration entity."""
        wav_file = attr.ib(type=WavFile)
        mode = attr.ib()
        offset = attr.ib()
        cooldown_period = attr.ib()
        cooldown_event = attr.ib()
        notify = attr.ib(repr=False)

        CONF_COOLDOWN = 'cooldown'
        CONF_COOLDOWN_PERIOD = 'period'
        CONF_COOLDOWN_EVENT = 'emit_event'
        CONF_PATH = 'path'
        CONF_MODE = 'mode'
        CONF_OFFSET = 'offset'

        DEFAULT_COOLDOWN_PERIOD = 10
        DEFAULT_COOLDOWN = {
            CONF_COOLDOWN_PERIOD: DEFAULT_COOLDOWN_PERIOD,
            CONF_COOLDOWN_EVENT: False
        }
        DEFAULT_MODE = MODE_PEARSON
        DEFAULT_OFFSET = 0.0

        WAV_FILE_SCHEMA = sc.Schema({
            CONF_PATH: sc.Use(str),
            sc.Optional(CONF_MODE, default=DEFAULT_MODE): sc.Use(str),
            sc.Optional(CONF_OFFSET, default=DEFAULT_OFFSET): sc.Use(float),
            sc.Optional(CONF_COOLDOWN, default=DEFAULT_COOLDOWN): {
                sc.Optional(CONF_COOLDOWN_PERIOD, default=DEFAULT_COOLDOWN_PERIOD):
                    sc.Use(parse_duration_literal),
                sc.Optional(CONF_COOLDOWN_EVENT, default=False): sc.Use(bool)
            }
        })

        WAV_FILE_LIST_SCHEMA = sc.Schema([WAV_FILE_SCHEMA])

        @classmethod
        def _check_mode(cls, mode):
            validator.one_of(ALLOWED_MODES, mode=mode)
            return mode

        @classmethod
        def from_dict(cls, dct_config, base_path, notify_fun, cooldown_fun):
            """Loads a wav configuration from a dictionary."""
            config = cls.WAV_FILE_SCHEMA.validate(dct_config)
            wav_file = WavFile.from_path(config[cls.CONF_PATH], base_path)
            cooldown_cfg = config[cls.CONF_COOLDOWN]
            cooldown_cb = None
            if cooldown_cfg[cls.CONF_COOLDOWN_EVENT]:
                cooldown_cb = partial(cooldown_fun, file_name=wav_file.file_name)
            return cls(
                wav_file=wav_file,
                mode=cls._check_mode(config[cls.CONF_MODE]),
                offset=config[cls.CONF_OFFSET],
                cooldown_period=cooldown_cfg[cls.CONF_COOLDOWN_PERIOD],
                cooldown_event=cooldown_cfg[cls.CONF_COOLDOWN_EVENT],
                notify=Cooldown(
                    notify_fun,
                    cool_down=cooldown_cfg[cls.CONF_COOLDOWN_PERIOD],
                    cool_down_callback=cooldown_cb
                )
            )

        @classmethod
        def from_list(cls, list_config, base_path, notify_fun, cooldown_fun):
            """Loads multiple wav configurations from a list."""
            validated = cls.WAV_FILE_LIST_SCHEMA.validate(list_config)
            return [
                cls.from_dict(wav_file, base_path, notify_fun, cooldown_fun)
                for wav_file in validated
            ]

    EXTRA = 'sound'

    RATE = 44100
    CHUNK_SIZE = 1024 * 4
    PEARSON_THRESHOLD = 0.5
    STD_THRESHOLD = 1.4

    def __init__(self, wav_files, device_index=None, ignore_overflow=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.wav_files = self.WavConfig.from_list(
            wav_files, self.base_path, self.notify, self._on_cooldown
        )
        self.device_index = device_index and int(device_index)
        self.ignore_overflow = bool(ignore_overflow)

    def _check_dependencies(self):
        load_optional_module('scipy.io.wavfile', self.EXTRA)
        load_optional_module('numpy', self.EXTRA)
        load_optional_module('scipy', self.EXTRA)
        load_optional_module('scipy.stats.stats', self.EXTRA)

    def _similarity(self, buffer, config: WavConfig):
        if config.mode == MODE_PEARSON:
            return similarity_pearson(
                buffer,
                config.wav_file,
                self.RATE,
                self.PEARSON_THRESHOLD + config.offset
            )
        if config.mode == MODE_STD:
            return similarity_std(
                buffer,
                config.wav_file,
                self.RATE,
                self.STD_THRESHOLD + config.offset
            )
        raise ValueError("The given mode '{}' is unsupported".format(config.mode))

    def _on_cooldown(self, file_name):
        self.notify({
            'type': 'cooldown',
            'sound': file_name
        })

    def pull(self):
        self._check_dependencies()
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
            buffers = [None for _ in self.wav_files]  # Init buffer foreach wav_file
            while not self.stopped:
                data = np.fromstring(stream.read(
                    self.CHUNK_SIZE,
                    exception_on_overflow=not self.ignore_overflow
                ), dtype=np.int16)

                for i, buffer in enumerate(buffers):
                    config = self.wav_files[i]
                    buffer = self._process_single(buffer, data, np, config)
                    buffers[i] = buffer
        finally:
            stream.close()
            pa.terminate()

            # Emit any pending cooldown events
            for config in self.wav_files:
                config.notify.execute_now()

    def _process_single(self, buffer, data, np, config):
        wav_file = config.wav_file
        N = wav_file.signal_length
        buffer = data if buffer is None else np.concatenate((buffer, data), axis=None)
        lbuf = len(buffer)
        if lbuf >= N:
            self.logger.debug("Buffer (%s): %s (Buffer) >= %s (Wav)",
                              wav_file.file_name, lbuf, N)
            flag, corrcoef, threshold = self._similarity(buffer, config)
            self.logger.debug("Correlation (%s): %s >= %s = %s",
                              wav_file.file_name, corrcoef, threshold, flag)
            if flag:
                config.notify({
                    'type': 'sound',
                    'sound': wav_file.file_name,
                    'corrcoef': corrcoef,
                    'threshold': threshold
                })
                buffer = None
            else:
                buffer = buffer[int(len(buffer) * 0.75):]

        return buffer
