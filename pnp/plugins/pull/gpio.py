import logging
import re
from abc import abstractmethod
from functools import partial

from . import PullBase
from ...utils import make_list, try_parse_int, auto_str, auto_str_ignore, Debounce, parse_duration_literal
from ...validator import Validator

logger = logging.getLogger(__name__)


CONST_AVAILABLE_GPIO_PINS = list(range(2, 28))
CONST_RISING_OPTIONS = ["rise", "rising"]
CONST_FALLING_OPTIONS = ["fall", "falling"]
CONST_SWITCH_OPTIONS = ["button", "switch"]
CONST_MOTION_OPTIONS = ["motion"]

CONST_RISING = "rising"
CONST_FALLING = "falling"
CONST_SWITCH = "switch"
CONST_MOTION_ON = "motion_on"
CONST_MOTION_OFF = "motion_off"


def load_gpio_package():
    try:
        try:
            import RPi.GPIO as GPIO
        except ImportError:
            from RPi import GPIO  # Only works for test cases when using the mocked package
    except ImportError:
        logger.warning("RPi.GPIO package is not available - Using mock")
        from ...mocking import GPIOMock as GPIO
    return GPIO


def str_to_gpio_pin(s):
    pin = try_parse_int(s)
    if not pin or pin not in CONST_AVAILABLE_GPIO_PINS:
        lmin = min(CONST_AVAILABLE_GPIO_PINS)
        lmax = max(CONST_AVAILABLE_GPIO_PINS)
        raise ValueError("The given string '{}' is not a valid GPIO pin. "
                         "String needs to be convertible to int and between {} and {}".format(s, lmin, lmax))
    return pin


def str_to_gpio_mode(s):
    cs = str(s)
    GPIO = load_gpio_package()
    if cs.lower() in CONST_RISING_OPTIONS:
        return GPIO.RISING
    if cs.lower() in CONST_FALLING_OPTIONS:
        return GPIO.FALLING
    raise ValueError("The given string '{}' is not a valid GPIO mode".format(cs))


def parse_mode_str(mode_str, regex, *groups):
    r = re.compile(regex)
    m = r.match(mode_str)
    if not m:
        raise ValueError("The given mode '{}' is not a valid definition for a callback".format(mode_str))
    return [m.group(g) for g in groups]


@auto_str(__repr__=True)
@auto_str_ignore(['_GPIO'])
class Callback:
    def __init__(self, gpio_pin):
        self._GPIO = None
        self.gpio_pin = str_to_gpio_pin(gpio_pin)

    @property
    def GPIO(self):
        if not self._GPIO:
            self._GPIO = load_gpio_package()
        return self._GPIO

    @classmethod
    def from_str(cls, candidate, default=CONST_RISING):
        gpio_pin_str, _, mode_str = str(candidate).partition(':')
        if not mode_str:
            mode_str = default
        if any(mode_str.lower().startswith(aswitch) for aswitch in CONST_RISING_OPTIONS):
            return RisingCallback.load(gpio_pin_str, mode_str)
        if any(mode_str.lower().startswith(aswitch) for aswitch in CONST_FALLING_OPTIONS):
            return FallingCallback.load(gpio_pin_str, mode_str)
        if any(mode_str.lower().startswith(aswitch) for aswitch in CONST_SWITCH_OPTIONS):
            return SwitchCallback.load(gpio_pin_str, mode_str)
        if any(mode_str.lower().startswith(aswitch) for aswitch in CONST_MOTION_OPTIONS):
            return MotionCallback.load(gpio_pin_str, mode_str)
        raise ValueError("The specified pin mode '{}' is not supported".format(mode_str))

    def _intercept(self, channel, direction, callback):
        callback(gpio_pin=channel, direction=direction)

    @abstractmethod
    def run(self, callback):
        raise NotImplementedError()  # pragma: no cover

    def stop(self):
        self.GPIO.remove_event_detect(self.gpio_pin)


class RisingCallback(Callback):
    DIRECTION = CONST_RISING

    @classmethod
    def load(cls, gpio_pin_str, mode_str):
        return cls(gpio_pin_str)

    def run(self, callback):
        self.GPIO.setup(self.gpio_pin, self.GPIO.IN)
        self.GPIO.add_event_detect(
            self.gpio_pin,
            str_to_gpio_mode(self.DIRECTION),
            callback=partial(self._intercept, direction=self.DIRECTION, callback=callback)
        )


class FallingCallback(RisingCallback):
    DIRECTION = CONST_FALLING


class SwitchCallback(Callback):
    BOUNCE_REGEX = r"^(switch|button)(\((?P<delay>\d+)\))?$"
    BOUNCE_GROUP = "delay"
    BOUNCE_DEFAULT = 500

    def __init__(self, gpio_pin, delay):
        super().__init__(gpio_pin)
        self.delay = int(delay)

    @classmethod
    def load(cls, gpio_pin_str, mode_str):
        delay, = parse_mode_str(mode_str, cls.BOUNCE_REGEX, cls.BOUNCE_GROUP)
        return cls(gpio_pin_str, delay or cls.BOUNCE_DEFAULT)

    def run(self, callback):
        self.GPIO.setup(self.gpio_pin, self.GPIO.IN)
        self.GPIO.add_event_detect(
            self.gpio_pin,
            self.GPIO.RISING,
            bouncetime=self.delay,
            callback=partial(self._intercept, direction=CONST_SWITCH, callback=callback)
        )


class MotionCallback(RisingCallback):
    DELAY_REGEX = r"^motion(\((?P<delay>\d+[sSmMhHdDwW]?)\))?$"
    DELAY_GROUP = "delay"
    DELAY_DEFAULT = "30s"

    def __init__(self, gpio_pin, delay):
        super().__init__(gpio_pin)
        self.delay = parse_duration_literal(delay)
        self._debouncer = None

    @classmethod
    def load(cls, gpio_pin_str, mode_str):
        delay, = parse_mode_str(mode_str, cls.DELAY_REGEX, cls.DELAY_GROUP)
        return cls(gpio_pin_str, delay or cls.DELAY_DEFAULT)

    def _motion_off(self, channel, callback):
        callback(gpio_pin=channel, direction=CONST_MOTION_OFF)
        self._debouncer = None

    def _intercept(self, channel, direction, callback):
        if self._debouncer is None:
            callback(gpio_pin=channel, direction=CONST_MOTION_ON)
            self._debouncer = Debounce(self._motion_off, self.delay)
        self._debouncer(channel, callback)

    def stop(self):
        if self._debouncer:
            self._debouncer.execute_now()


class Watcher(PullBase):
    __prefix__ = 'gpio'

    EXTRA = 'gpio'

    def __init__(self, pins, default=CONST_RISING, **kwargs):
        super().__init__(**kwargs)
        self._mode_default = default
        Validator.one_of(CONST_RISING_OPTIONS + CONST_FALLING_OPTIONS + CONST_SWITCH_OPTIONS + CONST_MOTION_OPTIONS,
                         mode_default=self._mode_default)
        self._pins = [Callback.from_str(pin_str, default=default) for pin_str in make_list(pins)]

    def _universal_callback(self, gpio_pin, direction):
        self.notify(dict(gpio_pin=gpio_pin, direction=direction))

    def pull(self):
        GPIO = load_gpio_package()
        GPIO.setmode(GPIO.BCM)

        try:
            for pin in self._pins:
                pin.run(self._universal_callback)
            while not self.stopped:
                self._sleep()
        finally:
            for pin in self._pins:
                pin.stop()
            GPIO.cleanup()
