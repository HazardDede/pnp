import logging
import re
from abc import abstractmethod
from collections import defaultdict, Counter
from functools import partial

from . import PullBase
from ...utils import (make_list, try_parse_int, auto_str, auto_str_ignore, Debounce, parse_duration_literal,
                      Singleton, Loggable)
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


class Watcher(PullBase):
    __prefix__ = 'gpio'

    EXTRA = 'gpio'

    def __init__(self, pins, default=CONST_RISING, **kwargs):
        super().__init__(**kwargs)
        self._mode_default = default
        Validator.one_of(CONST_RISING_OPTIONS + CONST_FALLING_OPTIONS + CONST_SWITCH_OPTIONS + CONST_MOTION_OPTIONS,
                         mode_default=self._mode_default)
        self._pins = [Callback.from_str(pin_str, default=default) for pin_str in make_list(pins)]
        _without_duplicate = set(self._pins)
        if len(_without_duplicate) != len(self._pins):
            diff = list((Counter(self._pins) - Counter(_without_duplicate)).elements())
            self.logger.warning("[{self.name}] You provided duplicate gpio pin configurations. Will ignore '{diff}'"
                                .format(**locals()))
            self._pins = _without_duplicate

    def _universal_callback(self, gpio_pin, event):
        self.logger.info("[{self.name}] GPIO '{gpio_pin}' raised event '{event}'".format(**locals()))
        self.notify(dict(gpio_pin=gpio_pin, event=event))

    def pull(self):
        GPIO = GPIOAdapter()

        try:
            for pin in self._pins:
                pin.run(self._universal_callback)
            GPIO.apply()
            while not self.stopped:
                self._sleep()
        finally:
            for pin in self._pins:
                pin.stop()
            GPIO.cleanup()


class GPIOAdapter (Singleton, Loggable):
    def __init__(self):
        self.logger.debug("GPIOWrapper __init__ called")
        self.GPIO = self._load_gpio_package()
        self.GPIO.setmode(self.GPIO.BCM)
        self._mchannel = dict()
        self._callbacks = defaultdict(list)

    def add_event_detect(self, channel, edge, callback, bouncetime=None):
        self._callbacks[channel].append((edge, callback, bouncetime))

    def apply(self):
        def safe_max(l):
            if not len(l):
                return None
            return max(l)

        for channel, ev in self._callbacks.items():
            self.GPIO.setup(channel, self.GPIO.IN)
            # If multiple bounce times are specified, use max
            max_bouncetime = safe_max([bouncetime for _, _, bouncetime in ev if bouncetime])
            edges = list(set([edge for edge, _, _ in ev]))
            edge = edges[0] if len(edges) == 1 else self.GPIO.BOTH

            # We have to use both mode because the pin is configured to use rising and falling.
            # But the callback does not provide the edge, so we have to guess in those cases ;-)
            if edge == self.GPIO.BOTH:
                self.logger.debug("Channel '{channel}' does provide rising and falling - Using 'both'".format(
                    **locals()))
                self._mchannel[channel] = None

            gpio_edge = self._str_to_gpio_mode(edge)
            if max_bouncetime:
                self.logger.debug("Channel '{channel}' uses bouncetime of {max_bouncetime}ms. "
                                  "This will apply for all callbacks".format(**locals()))
                self.GPIO.add_event_detect(channel, gpio_edge, bouncetime=max_bouncetime)
            else:
                self.GPIO.add_event_detect(channel, gpio_edge)

            self.GPIO.add_event_callback(channel, self._dispatcher)

    def remove_event_detect(self, channel):
        self._mchannel.pop(channel, None)
        self._callbacks.pop(channel, None)
        return self.GPIO.remove_event_detect(channel)

    def cleanup(self):
        self._mchannel.clear()
        self._callbacks.clear()
        return self.GPIO.cleanup()

    def _dispatcher(self, channel):
        callbacks = self._callbacks.get(channel, None)
        if not callbacks:
            return
        is_multi_channel = channel in self._mchannel
        current_edge = None
        if is_multi_channel:
            last_state = self._mchannel[channel] or CONST_FALLING
            current_edge = CONST_RISING if last_state == CONST_FALLING else CONST_FALLING
            self._mchannel[channel] = current_edge

        for cb_edge, cb, _ in callbacks:
            if current_edge is None or cb_edge == current_edge:
                cb(channel)

    def _str_to_gpio_mode(self, s):
        if s == self.GPIO.BOTH:
            return s
        cs = str(s)
        if cs.lower() in CONST_RISING_OPTIONS:
            return self.GPIO.RISING
        if cs.lower() in CONST_FALLING_OPTIONS:
            return self.GPIO.FALLING
        raise ValueError("The given string '{}' is not a valid GPIO mode".format(cs))

    @staticmethod
    def _load_gpio_package():
        try:
            try:
                import RPi.GPIO as GPIO
            except ImportError:
                from RPi import GPIO  # Only works for test cases when using the mocked package
        except ImportError:  # pragma: no cover
            logger.warning("RPi.GPIO package is not available - Using mock")
            from ...mocking import GPIOMock as GPIO
        return GPIO


@auto_str(__repr__=True)
@auto_str_ignore(['_GPIO'])
class Callback:
    def __init__(self, gpio_pin):
        self.gpio_pin = self._str_to_gpio_pin(gpio_pin)

    @property
    def GPIO(self):
        return GPIOAdapter()

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

    def _intercept(self, channel, event, callback):
        callback(gpio_pin=channel, event=event)

    @abstractmethod
    def run(self, callback):
        raise NotImplementedError()  # pragma: no cover

    def stop(self):
        self.GPIO.remove_event_detect(self.gpio_pin)

    def _eqstr(self):
        # If we have multiple switches or motion for the same pin only one will applied
        # We basically account for the pin and the class only without additional params.
        return "{}({})".format(type(self).__name__, str(self.gpio_pin))

    @staticmethod
    def _parse_mode_str(mode_str, regex, *groups):
        r = re.compile(regex)
        m = r.match(mode_str)
        if not m:
            raise ValueError("The given mode '{}' is not a valid definition for a callback".format(mode_str))
        return [m.group(g) for g in groups]

    @staticmethod
    def _str_to_gpio_pin(s):
        pin = try_parse_int(s)
        if not pin or pin not in CONST_AVAILABLE_GPIO_PINS:
            lmin = min(CONST_AVAILABLE_GPIO_PINS)
            lmax = max(CONST_AVAILABLE_GPIO_PINS)
            raise ValueError("The given string '{}' is not a valid GPIO pin. "
                             "String needs to be convertible to int and between {} and {}".format(s, lmin, lmax))
        return pin

    def __hash__(self):
        return hash(str(self._eqstr()))

    def __eq__(self, other):
        if not hasattr(other, '_eqstr'):  # pragma: no cover
            return False
        return self._eqstr() == other._eqstr()


class RisingCallback(Callback):
    EDGE = CONST_RISING

    @classmethod
    def load(cls, gpio_pin_str, mode_str):
        return cls(gpio_pin_str)

    def run(self, callback):
        self.GPIO.add_event_detect(
            self.gpio_pin,
            self.EDGE,
            callback=partial(self._intercept, event=self.EDGE, callback=callback)
        )


class FallingCallback(RisingCallback):
    EDGE = CONST_FALLING


class SwitchCallback(Callback):
    EDGE = CONST_RISING
    BOUNCE_REGEX = r"^(switch|button)(\((?P<delay>\d+)\))?$"
    BOUNCE_GROUP = "delay"
    BOUNCE_DEFAULT = 500

    def __init__(self, gpio_pin, delay):
        super().__init__(gpio_pin)
        self.delay = int(delay)

    @classmethod
    def load(cls, gpio_pin_str, mode_str):
        delay, = cls._parse_mode_str(mode_str, cls.BOUNCE_REGEX, cls.BOUNCE_GROUP)
        return cls(gpio_pin_str, delay or cls.BOUNCE_DEFAULT)

    def run(self, callback):
        self.GPIO.add_event_detect(
            self.gpio_pin,
            self.EDGE,
            bouncetime=self.delay,
            callback=partial(self._intercept, event=CONST_SWITCH, callback=callback)
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
        delay, = cls._parse_mode_str(mode_str, cls.DELAY_REGEX, cls.DELAY_GROUP)
        return cls(gpio_pin_str, delay or cls.DELAY_DEFAULT)

    def _motion_off(self, channel, callback):
        callback(gpio_pin=channel, event=CONST_MOTION_OFF)
        self._debouncer = None

    def _intercept(self, channel, event, callback):
        if event == CONST_RISING:
            if self._debouncer is None:
                callback(gpio_pin=channel, event=CONST_MOTION_ON)
                self._debouncer = Debounce(self._motion_off, self.delay)
            self._debouncer(channel, callback)

    def stop(self):
        if self._debouncer:
            self._debouncer.execute_now()
