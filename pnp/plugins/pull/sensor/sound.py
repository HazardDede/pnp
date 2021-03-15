"""Pull: sensor.Sound"""

from functools import partial
from typing import Any, Optional, List, Dict, Tuple

import numpy as np
import pyaudio
import pydantic
import schema as sc

from pnp import validator
from pnp.plugins.pull import SyncPull
from pnp.shared.sound import (
    WavFile,
    similarity_pearson,
    similarity_std,
    MODE_PEARSON,
    MODE_STD,
    ALLOWED_MODES, NumpyNDArray
)
from pnp.utils import (
    parse_duration_literal,
    Cooldown
)

__EXTRA__ = 'sound'


class WavConfig(pydantic.BaseModel):
    """Wav configuration entity."""
    wav_file: WavFile
    mode: str
    offset: float
    cooldown_period: int
    cooldown_event: bool
    notify: Cooldown

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

    @pydantic.validator('mode')
    @classmethod
    def _check_mode(cls, mode: str) -> str:
        validator.one_of(ALLOWED_MODES, mode=mode)
        return mode


class WavConfigSchema:
    """Wav configuration configuration schema."""

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
    def from_dict(
            cls, dct_config: Dict[str, Any], base_path: str, notify_fun: Any,
            cooldown_fun: Any
    ) -> 'WavConfig':
        """Loads a wav configuration from a dictionary."""
        config = cls.WAV_FILE_SCHEMA.validate(dct_config)
        wav_file = WavFile.from_path(config[cls.CONF_PATH], base_path)
        cooldown_cfg = config[cls.CONF_COOLDOWN]
        cooldown_cb = None
        if cooldown_cfg[cls.CONF_COOLDOWN_EVENT]:
            cooldown_cb = partial(cooldown_fun, file_name=wav_file.file_name)
        return WavConfig(
            wav_file=wav_file,
            mode=config[cls.CONF_MODE],
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
    def from_list(
            cls, list_config: List[Dict[str, Any]], base_path: str, notify_fun: Any,
            cooldown_fun: Any
    ) -> List[WavConfig]:
        """Loads multiple wav configurations from a list."""
        validated = cls.WAV_FILE_LIST_SCHEMA.validate(list_config)
        return [
            cls.from_dict(wav_file, base_path, notify_fun, cooldown_fun)
            for wav_file in validated
        ]


# pylint: disable=too-many-instance-attributes
class Sound(SyncPull):
    """
    Listens to the microphone in realtime and searches the stream for a specific sound pattern.
    Practical example: I use this plugin to recognize my doorbell without tampering with
    the electrical device ;-)

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#sensor-sound
    """

    __REPR_FIELDS__ = ['device_index', 'ignore_overflow', 'wav_files']

    RATE = 44100
    CHUNK_SIZE = 1024 * 4
    PEARSON_THRESHOLD = 0.5
    STD_THRESHOLD = 1.4

    def __init__(
            self, wav_files: List[Dict[str, Any]], device_index: Optional[int] = None,
            ignore_overflow: bool = False, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.wav_files = WavConfigSchema.from_list(
            wav_files, self.base_path, self.notify, self._on_cooldown
        )
        self.device_index = device_index and int(device_index)
        self.ignore_overflow = bool(ignore_overflow)

    def _similarity(self, buffer: NumpyNDArray, config: WavConfig) -> Tuple[bool, float, float]:
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

    def _on_cooldown(self, file_name: str) -> None:
        self.notify({
            'type': 'cooldown',
            'sound': file_name
        })

    def _pull(self) -> None:
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
                    buffer = self._process_single(buffer, data, config)
                    buffers[i] = buffer
        finally:
            stream.close()
            pa.terminate()

            # Emit any pending cooldown events
            for config in self.wav_files:
                config.notify.execute_now()

    def _process_single(
            self, buffer: NumpyNDArray, data: NumpyNDArray, config: WavConfig
    ) -> NumpyNDArray:
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
