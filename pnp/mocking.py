import random

from collections import defaultdict


class DHTMock:
    DHT22 = "dht22"
    DHT11 = "dht11"
    AM2302 = "am2302"

    @staticmethod
    def read_retry(sensor, pin):
        return round(random.uniform(1, 100), 2), round(random.uniform(8, 36), 2)  # pragma: no cover


class GPIOMock:  # pragma: no cover
    BCM = "bcm"
    IN = "in"
    RISING = "rising"
    FALLING = "falling"
    BOTH = "both"

    MODES = dict()
    CALLBACKS = defaultdict(list)
    SETUPS = set()

    @classmethod
    def setmode(cls, mode):
        pass

    @classmethod
    def setup(cls, channel, in_out):
        if channel in cls.SETUPS:
            raise RuntimeError("You called setup more than one time for channel '{}'".format(channel))
        cls.SETUPS.add(channel)

    @classmethod
    def cleanup(cls):
        pass

    @classmethod
    def add_event_detect(cls, channel, mode, callback=None, bouncetime=None):
        if channel not in cls.SETUPS:
            raise RuntimeError("You did not setup the channel '{}' before activating event detection".format(channel))
        cls.MODES[channel] = mode
        if not callback:
            return
        if channel in cls.CALLBACKS:
            raise RuntimeError("You already added a callback to this channel")
        cls.CALLBACKS[channel].append((callback, mode))

    @classmethod
    def add_event_callback(cls, channel, callback):
        if channel not in cls.MODES:
            raise RuntimeError("You have to enable the event detection first")
        mode = cls.MODES[channel]
        cls.CALLBACKS[channel].append((callback, mode))

    @classmethod
    def remove_event_detect(cls, channel):
        cls.CALLBACKS.pop(channel, None)
        cls.MODES.pop(channel, None)

    @classmethod
    def clear(cls):
        cls.MODES.clear()
        cls.CALLBACKS.clear()
        cls.SETUPS.clear()

    @classmethod
    def fire_event(cls, channel, mode):
        for cb, cb_mode in cls.CALLBACKS[channel]:
            if mode == cb_mode or cb_mode == cls.BOTH:
                cb(channel)


class PyAudioMock:  # pragma: no cover
    class StreamMock:
        def __init__(self, wav_file):
            self.wav_file = wav_file
            self.fh = open(self.wav_file, 'rb')

        def read(self, chunk_size):
            res = self.fh.read()
            self.fh.seek(0)
            return res

        def close(self):
            self.fh.close()

    def __init__(self, mock_wav):
        self.mock_wav = str(mock_wav)

    def __call__(self):
        return self

    def open(self, **kwargs):
        return self.StreamMock(self.mock_wav)

    def terminate(self):
        pass
