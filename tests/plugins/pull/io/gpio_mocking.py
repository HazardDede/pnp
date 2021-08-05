from collections import defaultdict


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
