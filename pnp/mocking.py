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

    CALLBACKS = defaultdict(list)

    @classmethod
    def setmode(cls, mode):
        pass

    @classmethod
    def setup(cls, channel, in_out):
        pass

    @classmethod
    def cleanup(cls):
        pass

    @classmethod
    def add_event_detect(cls, channel, mode, callback, bouncetime=None):
        cls.CALLBACKS[channel].append((callback, mode))

    @classmethod
    def remove_event_detect(cls, channel):
        cls.CALLBACKS.pop(channel, None)

    @classmethod
    def clear_callbacks(cls):
        cls.CALLBACKS.clear()

    @classmethod
    def fire_event(cls, channel, mode):
        for cb, cb_mode in cls.CALLBACKS[channel]:
            if mode == cb_mode:
                cb(channel)
