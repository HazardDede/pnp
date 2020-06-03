"""GPIO related plugins."""

from collections import Counter

from pnp import validator
from pnp.plugins.pull import PullBase
from pnp.shared.gpio import (
    CONST_RISING, CONST_RISING_OPTIONS, CONST_FALLING_OPTIONS,
    CONST_SWITCH_OPTIONS, CONST_MOTION_OPTIONS, Callback, GPIOAdapter
)
from pnp.utils import (make_list)


class Watcher(PullBase):
    """
    Listens for low/high state changes on the configured gpio pins.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/gpio.Watcher/index.md
    """

    EXTRA = 'gpio'

    def __init__(self, pins, default=CONST_RISING, **kwargs):
        super().__init__(**kwargs)
        self._mode_default = default
        validator.one_of(
            CONST_RISING_OPTIONS + CONST_FALLING_OPTIONS + CONST_SWITCH_OPTIONS
            + CONST_MOTION_OPTIONS,
            mode_default=self._mode_default
        )
        self._pins = [Callback.from_str(pin_str, default=default) for pin_str in make_list(pins)]
        _without_duplicate = set(self._pins)
        if len(_without_duplicate) != len(self._pins):
            diff = list((Counter(self._pins) - Counter(_without_duplicate)).elements())
            self.logger.warning(
                "You provided duplicate gpio pin configurations. Will ignore '%s'", diff
            )
            self._pins = _without_duplicate

    def _universal_callback(self, gpio_pin, event):
        self.logger.info("GPIO '%s' raised event '%s'", gpio_pin, event)
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
