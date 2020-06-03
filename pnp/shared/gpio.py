"""Shared functionality for gpio related stuff."""

import logging
import re
from abc import abstractmethod
from collections import defaultdict
from functools import partial
from typing import Optional, Iterable, Any, Callable, Dict, Tuple, List, Union

from pnp.typing import DurationLiteral
from pnp.utils import (
    try_parse_int, auto_str, auto_str_ignore, Debounce, parse_duration_literal, Singleton,
    Loggable
)

_LOGGER = logging.getLogger(__name__)

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

Channel = int
Edge = str
Bounce = int
EventCallback = Callable[[Channel], None]
InterceptCallback = Callable[[Channel, Edge], None]
CallbackDict = Dict[Channel, List[Tuple[Edge, EventCallback, Optional[int]]]]


class GPIOAdapter(Singleton, Loggable):
    """Convenience wrapper around the RPi.GPIO package."""

    def __init__(self) -> None:
        super().__init__()
        self.logger.debug("GPIOWrapper __init__ called")
        self.GPIO = self._load_gpio_package()
        self.GPIO.setmode(self.GPIO.BCM)
        self._mchannel = dict()  # type: Dict[Channel, Optional[Edge]]
        self._callbacks = defaultdict(list)  # type: CallbackDict

    def add_event_detect(
        self, channel: Channel, edge: Edge, callback: EventCallback,
        bouncetime: Optional[Bounce] = None
    ) -> None:
        """Adds a callback when the state of the channel changes."""
        self._callbacks[channel].append((edge, callback, bouncetime))

    def apply(self) -> None:
        """Applies the configured callbacks."""
        def safe_max(lst: Iterable[Bounce]) -> Optional[Bounce]:
            if not lst:
                return None
            return max(lst)

        for channel, event in self._callbacks.items():
            self.GPIO.setup(channel, self.GPIO.IN)
            # If multiple bounce times are specified, use max
            max_bouncetime = safe_max([bouncetime for _, _, bouncetime in event if bouncetime])
            edges = list({edge for edge, _, _ in event})
            edge = edges[0] if len(edges) == 1 else self.GPIO.BOTH

            # We have to use both mode because the pin is configured to use rising and falling.
            # But the callback does not provide the edge, so we have to guess in those cases ;-)
            if edge == self.GPIO.BOTH:
                self.logger.debug(
                    "Channel '%s' does provide rising and falling - Using 'both'", channel
                )
                self._mchannel[channel] = None

            gpio_edge = self._str_to_gpio_mode(edge)
            if max_bouncetime:
                self.logger.debug("Channel '%s' uses bouncetime of %sms. "
                                  "This will apply for all callbacks", channel, max_bouncetime)
                self.GPIO.add_event_detect(channel, gpio_edge, bouncetime=max_bouncetime)
            else:
                self.GPIO.add_event_detect(channel, gpio_edge)

            self.GPIO.add_event_callback(channel, self._dispatcher)

    def remove_event_detect(self, channel: Channel) -> None:
        """Removes a previously added callback."""
        self._mchannel.pop(channel, None)
        self._callbacks.pop(channel, None)
        self.GPIO.remove_event_detect(channel)

    def cleanup(self) -> None:
        """Clean up the mess you have done."""
        self._mchannel.clear()
        self._callbacks.clear()
        self.GPIO.cleanup()

    def _dispatcher(self, channel: Channel) -> None:
        callbacks = self._callbacks.get(channel, None)
        if not callbacks:
            return
        is_multi_channel = channel in self._mchannel
        current_edge = None
        if is_multi_channel:
            last_state = self._mchannel[channel] or CONST_FALLING
            current_edge = CONST_RISING if last_state == CONST_FALLING else CONST_FALLING
            self._mchannel[channel] = current_edge

        for cb_edge, cback, _ in callbacks:
            if current_edge is None or cb_edge == current_edge:
                cback(channel)

    def _str_to_gpio_mode(self, _str: str) -> Edge:
        if _str == self.GPIO.BOTH:
            return _str
        _str = str(_str)
        if _str.lower() in CONST_RISING_OPTIONS:
            return self.GPIO.RISING  # type: ignore
        if _str.lower() in CONST_FALLING_OPTIONS:
            return self.GPIO.FALLING  # type: ignore
        raise ValueError("The given string '{}' is not a valid GPIO mode".format(_str))

    @staticmethod
    def _load_gpio_package() -> Any:
        try:
            try:
                import RPi.GPIO as GPIO
            except ImportError:
                from RPi import GPIO  # Only works for test cases when using the mocked package
        except ImportError:  # pragma: no cover
            _LOGGER.warning("RPi.GPIO package is not available - Using mock")
            from ..mocking import GPIOMock as GPIO  # type: ignore
        return GPIO


@auto_str(__repr__=True)
@auto_str_ignore(['_GPIO'])
class Callback:
    """Base class for a gpio callback."""
    def __init__(self, gpio_pin: str):
        self.gpio_pin = self._str_to_gpio_pin(gpio_pin)

    @property
    def GPIO(self) -> GPIOAdapter:
        """Return the gpio wrapper."""
        return GPIOAdapter()

    @classmethod
    def load(cls, gpio_pin_str: str, mode_str: str) -> 'Callback':
        """Make an instance using the gpio_pin as a string. Override in child classes
        to perform some validation checks."""
        raise NotImplementedError()

    @classmethod
    def from_str(cls, candidate: Any, default: str = CONST_RISING) -> 'Callback':
        """Load the callback from a string."""
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

    def _intercept(self, channel: Channel, event: Edge, callback: InterceptCallback) -> None:
        _ = self  # Fake usage
        callback(channel, event)

    @abstractmethod
    def run(self, callback: InterceptCallback) -> None:
        """Registers this callback to the gpio wrapper."""
        raise NotImplementedError()  # pragma: no cover

    def stop(self) -> None:
        """Stop this callback to receive events."""
        self.GPIO.remove_event_detect(self.gpio_pin)

    def _eqstr(self) -> str:
        # If we have multiple switches or motion for the same pin only one will applied
        # We basically account for the pin and the class only without additional params.
        return "{}({})".format(type(self).__name__, str(self.gpio_pin))

    @staticmethod
    def _parse_mode_str(mode_str: str, regex: str, *groups: str) -> Iterable[str]:
        _rgx = re.compile(regex)
        _match = _rgx.match(mode_str)
        if not _match:
            raise ValueError("The given mode '{}' is not a valid definition for a callback"
                             .format(mode_str))
        return [_match.group(g) for g in groups]

    @staticmethod
    def _str_to_gpio_pin(_str: str) -> Channel:
        pin = try_parse_int(_str)
        if not pin or pin not in CONST_AVAILABLE_GPIO_PINS:
            lmin = min(CONST_AVAILABLE_GPIO_PINS)
            lmax = max(CONST_AVAILABLE_GPIO_PINS)
            raise ValueError("The given string '{}' is not a valid GPIO pin. "
                             "String needs to be convertible to int and between {} and {}"
                             .format(_str, lmin, lmax))
        return pin

    def __hash__(self) -> int:
        return hash(str(self._eqstr()))

    def __eq__(self, other: Any) -> bool:
        if not hasattr(other, '_eqstr'):  # pragma: no cover
            return False
        return bool(self._eqstr() == other._eqstr())  # pylint: disable=protected-access


class RisingCallback(Callback):
    """Callback when the gpio channel switches to high."""
    EDGE = CONST_RISING

    @classmethod
    def load(cls, gpio_pin_str: str, mode_str: str) -> 'Callback':
        """Make an instance using the gpio_pin as a string."""
        return cls(gpio_pin_str)

    def run(self, callback: InterceptCallback) -> None:
        self.GPIO.add_event_detect(
            self.gpio_pin,
            self.EDGE,
            callback=partial(self._intercept, event=self.EDGE, callback=callback)
        )


class FallingCallback(RisingCallback):
    """Callback when the gpio channel switches to low."""
    EDGE = CONST_FALLING


class SwitchCallback(Callback):
    """Callback when the gpio channel switches to high with some bounce delay."""
    EDGE = CONST_RISING
    BOUNCE_REGEX = r"^(switch|button)(\((?P<delay>\d+)\))?$"
    BOUNCE_GROUP = "delay"
    BOUNCE_DEFAULT = 500

    def __init__(self, gpio_pin: str, delay: Union[Bounce, DurationLiteral]):
        super().__init__(gpio_pin)
        self.delay = int(delay)

    @classmethod
    def load(cls, gpio_pin_str: str, mode_str: str) -> 'Callback':
        """Make an instance using the gpio_pin as a string."""
        delay, = cls._parse_mode_str(mode_str, cls.BOUNCE_REGEX, cls.BOUNCE_GROUP)
        return cls(gpio_pin_str, delay or cls.BOUNCE_DEFAULT)

    def run(self, callback: InterceptCallback) -> None:
        self.GPIO.add_event_detect(
            self.gpio_pin,
            self.EDGE,
            bouncetime=self.delay,
            callback=partial(self._intercept, event=CONST_SWITCH, callback=callback)
        )


class MotionCallback(RisingCallback):
    """Callback when the gpio channel switches to high. When the gpio channel switches back to low
    the callback will emit an motion off event after some predefined delay."""
    DELAY_REGEX = r"^motion(\((?P<delay>\d+[sSmMhHdDwW]?)\))?$"
    DELAY_GROUP = "delay"
    DELAY_DEFAULT = "30s"

    def __init__(self, gpio_pin: str, delay: str):
        super().__init__(gpio_pin)
        self.delay = parse_duration_literal(delay)
        self._debouncer = None  # type: Optional[Debounce]

    @classmethod
    def load(cls, gpio_pin_str: str, mode_str: str) -> 'Callback':
        """Make an instance using the gpio_pin as a string."""
        delay, = cls._parse_mode_str(mode_str, cls.DELAY_REGEX, cls.DELAY_GROUP)
        return cls(gpio_pin_str, delay or cls.DELAY_DEFAULT)

    def _motion_off(self, channel: Channel, callback: InterceptCallback) -> None:
        callback(channel, CONST_MOTION_OFF)
        self._debouncer = None

    def _intercept(self, channel: Channel, event: Edge, callback: InterceptCallback) -> None:
        if event == CONST_RISING:
            if self._debouncer is None:
                callback(channel, CONST_MOTION_ON)
                self._debouncer = Debounce(self._motion_off, self.delay)
            self._debouncer(channel, callback)

    def stop(self) -> None:
        if self._debouncer:
            self._debouncer.execute_now()
