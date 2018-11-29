import sys
import types

import time

import pytest

import pnp.plugins.pull.gpio as gpio
from pnp.utils import parse_duration_literal
from tests.plugins.helper import make_runner, start_runner
from pnp.mocking import GPIOMock


@pytest.yield_fixture(scope='function')
def mock_gpio():
    # Mock the whole RPi.GPIO Module - that one isn't even available on non-arm architectures
    module_name = 'RPi'
    mock_rpi_gpio = types.ModuleType(module_name)
    sys.modules[module_name] = mock_rpi_gpio
    mock_rpi_gpio.GPIO = GPIOMock
    yield mock_rpi_gpio.GPIO
    GPIOMock.clear_callbacks()


def test_gpio_pull_for_smoke(mock_gpio):
    dut = gpio.Watcher(["2:rising", "3:falling", "4:switch"], name='pytest')

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)
        mock_gpio.fire_event(2, mock_gpio.RISING)
        mock_gpio.fire_event(3, mock_gpio.FALLING)
        mock_gpio.fire_event(4, mock_gpio.RISING)
        time.sleep(0.5)

    assert len(events) == 3
    assert events[0] == {'gpio_pin': 2, 'direction': 'rising'}
    assert events[1] == {'gpio_pin': 3, 'direction': 'falling'}
    assert events[2] == {'gpio_pin': 4, 'direction': 'switch'}


def test_gpio_pull_with_motion_debounce(mock_gpio):
    dut = gpio.Watcher("2:motion(1s)", name='pytest')

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)
        for _ in range(10):
            mock_gpio.fire_event(2, mock_gpio.RISING)
        time.sleep(1.2)
        mock_gpio.fire_event(2, mock_gpio.RISING)
        time.sleep(0.5)

    assert len(events) == 4
    assert events[0] == {'gpio_pin': 2, 'direction': 'motion_on'}
    assert events[1] == {'gpio_pin': 2, 'direction': 'motion_off'}
    assert events[0] == {'gpio_pin': 2, 'direction': 'motion_on'}
    assert events[1] == {'gpio_pin': 2, 'direction': 'motion_off'}


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
