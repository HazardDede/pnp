import pnp.shared.gpio as gpio
from pnp.utils import parse_duration_literal


def test_callback_from_str():
    res = gpio.Callback.from_str("2")
    assert isinstance(res, gpio.RisingCallback)
    assert res.gpio_pin == 2

    res = gpio.Callback.from_str("2", default=gpio.CONST_FALLING)
    assert isinstance(res, gpio.FallingCallback)
    assert res.gpio_pin == 2

    res = gpio.Callback.from_str("2:rising", default=gpio.CONST_FALLING)
    assert isinstance(res, gpio.RisingCallback)
    assert res.gpio_pin == 2

    res = gpio.Callback.from_str("2:falling", default=gpio.CONST_RISING)
    assert isinstance(res, gpio.FallingCallback)
    assert res.gpio_pin == 2

    res = gpio.Callback.from_str("2:switch", default=gpio.CONST_RISING)
    assert isinstance(res, gpio.SwitchCallback)
    assert res.gpio_pin == 2
    assert res.delay == gpio.SwitchCallback.BOUNCE_DEFAULT

    res = gpio.Callback.from_str("2:switch(999)", default=gpio.CONST_RISING)
    assert isinstance(res, gpio.SwitchCallback)
    assert res.gpio_pin == 2
    assert res.delay == 999

    try:
        gpio.Callback.from_str("2:switch()", default=gpio.CONST_RISING)
    except ValueError:
        pass

    res = gpio.Callback.from_str("2:motion", default=gpio.CONST_RISING)
    assert isinstance(res, gpio.MotionCallback)
    assert res.gpio_pin == 2
    assert res.delay == parse_duration_literal(gpio.MotionCallback.DELAY_DEFAULT)

    res = gpio.Callback.from_str("2:motion(2m)", default=gpio.CONST_RISING)
    assert isinstance(res, gpio.MotionCallback)
    assert res.gpio_pin == 2
    assert res.delay == 120

    try:
        gpio.Callback.from_str("2:motion()", default=gpio.CONST_RISING)
    except ValueError:
        pass
