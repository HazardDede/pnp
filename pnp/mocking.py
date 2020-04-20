"""Some mocking stuff for packages that are not available on every platform (just for testing)."""

import random

from collections import defaultdict


class DHTMock:
    """Mocks a DHT device (only available on rpi's)."""
    DHT22 = "dht22"
    DHT11 = "dht11"
    AM2302 = "am2302"

    @staticmethod
    def read_retry(sensor, pin):  # pylint: disable=unused-argument
        """Read the sensor values (humidity, temperature)."""
        return (
            round(random.uniform(1, 100), 2),
            round(random.uniform(8, 36), 2)
        )  # pragma: no cover


class GPIOMock:  # pragma: no cover
    """Mocks the RPi.GPIO (only available on rpi)."""
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
        """Set the mode."""

    @classmethod
    def setup(cls, channel, in_out):  # pylint: disable=unused-argument
        """Setup the given gpio channel."""
        if channel in cls.SETUPS:
            raise RuntimeError(
                "You called setup more than one time for channel '{}'".format(channel)
            )
        cls.SETUPS.add(channel)

    @classmethod
    def cleanup(cls):
        """Free the resources."""

    @classmethod
    def add_event_detect(cls, channel, mode, callback=None, bouncetime=None):  # pylint: disable=unused-argument
        """Adds an event detection callback when the state of the gpio channels changes."""
        if channel not in cls.SETUPS:
            raise RuntimeError(
                "You did not setup the channel '{}' before activating event "
                "detection".format(channel)
            )
        cls.MODES[channel] = mode
        if not callback:
            return
        if channel in cls.CALLBACKS:
            raise RuntimeError("You already added a callback to this channel")
        cls.CALLBACKS[channel].append((callback, mode))

    @classmethod
    def add_event_callback(cls, channel, callback):
        """Adds an event detection callback when the state of the gpio channels changes."""
        if channel not in cls.MODES:
            raise RuntimeError("You have to enable the event detection first")
        mode = cls.MODES[channel]
        cls.CALLBACKS[channel].append((callback, mode))

    @classmethod
    def remove_event_detect(cls, channel):
        """Remove all callbacks from the event detection for the given gpio channel."""
        cls.CALLBACKS.pop(channel, None)
        cls.MODES.pop(channel, None)

    @classmethod
    def clear(cls):
        """Clear this instance for re-use."""
        cls.MODES.clear()
        cls.CALLBACKS.clear()
        cls.SETUPS.clear()

    @classmethod
    def fire_event(cls, channel, mode):
        """Fire an event in the specified mode for the given gpio channel."""
        for cback, cb_mode in cls.CALLBACKS[channel]:
            if cb_mode in (cls.BOTH, mode):
                cback(channel)


class FritzBoxHostsMock:  # pragma: no cover
    """Mocks the fritzconnection.FritzHosts class."""
    def __init__(self):
        self.address = None
        self.user = None
        self.password = None
        self.calls = 0

    def __call__(self, address, user, password):
        """The actual instantiation of mock from a client perspective."""
        self.address = address
        self.user = user
        self.password = password
        return self

    @property
    def modelname(self):
        """Return the name of the fritzbox model / make."""
        return "Fritz!Box Mock v1.0"

    def get_hosts_info(self):
        """Return the known hosts."""
        _ = self  # Fake usage
        self.calls += 1
        return [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:13", 'ip': '192.168.178.11', 'name': 'pc2', 'status': False},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3',
             'status': self.calls <= 1}
        ]

    def get_specific_host_entry(self, mac_address):
        """Return the host associated to the given mac address."""
        if mac_address == '12:34:56:78:14':
            self.calls += 1
        _map = {
            '12:34:56:78:12': {
                'NewIPAddress': '192.168.178.10', 'NewActive': True, 'NewHostName': 'pc1'
            },
            '12:34:56:78:13': {
                'NewIPAddress': '192.168.178.11', 'NewActive': False, 'NewHostName': 'pc2'
            },
            '12:34:56:78:14': {
                'NewIPAddress': '192.168.178.12', 'NewActive': self.calls <= 1, 'NewHostName': 'pc3'
            }
        }
        return _map[mac_address]


class PyAudioMock:  # pragma: no cover
    """Mocks the pyaudio package (only available with audio devices)."""
    class _StreamMock:
        def __init__(self, wav_file):
            self.wav_file = wav_file
            self.fhandle = open(self.wav_file, 'rb')

        def read(self, chunk_size, exception_on_overflow):  # pylint: disable=unused-argument
            """Read from the stream."""
            res = self.fhandle.read()
            self.fhandle.seek(0)
            return res

        def close(self):
            """Close the stream."""
            self.fhandle.close()

    def __init__(self, mock_wav):
        self.mock_wav = str(mock_wav)

    def __call__(self):
        return self

    def open(self, **kwargs):  # pylint: disable=unused-argument
        """Open a audio stream."""
        return self._StreamMock(self.mock_wav)

    def terminate(self):
        """Terminate the audio stream."""
