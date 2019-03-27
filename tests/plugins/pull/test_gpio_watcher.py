import sys
import time
import types

import pytest

import pnp.plugins.pull.gpio as gpio
import pnp.shared.gpio as shared
from pnp.mocking import GPIOMock
from pnp.utils import parse_duration_literal
from . import make_runner, start_runner


@pytest.yield_fixture(scope='function')
def mock_gpio():
    # Mock the whole RPi.GPIO Module - that one isn't even available on non-arm architectures
    module_name = 'RPi'
    mock_rpi_gpio = types.ModuleType(module_name)
    sys.modules[module_name] = mock_rpi_gpio
    mock_rpi_gpio.GPIO = GPIOMock
    yield mock_rpi_gpio.GPIO
    GPIOMock.clear()


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
    assert events[0] == {'gpio_pin': 2, 'event': 'rising'}
    assert events[1] == {'gpio_pin': 3, 'event': 'falling'}
    assert events[2] == {'gpio_pin': 4, 'event': 'switch'}


def test_gpio_pull_for_duplicate_pins(mock_gpio):
    dut = gpio.Watcher(["2:rising", "2:falling", "2:rising"], name='pytest')
    assert len(dut._pins) == 2

    dut = gpio.Watcher(["2:rising", "2:rising", "2:rising"], name='pytest')
    assert len(dut._pins) == 1

    dut = gpio.Watcher(["2:falling", "2:falling"], name='pytest')
    assert len(dut._pins) == 1

    dut = gpio.Watcher(["2:switch(500)", "2:switch(1000)", "2:rising"], name='pytest')
    assert len(dut._pins) == 2

    dut = gpio.Watcher(["2:motion(1s)", "2:motion(5s)", "2:rising"], name='pytest')
    assert len(dut._pins) == 2


def test_gpio_with_rising_falling_on_same_pin(mock_gpio):
    dut = gpio.Watcher(["2:rising", "2:falling"], name='pytest')

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)
        mock_gpio.fire_event(2, mock_gpio.RISING)
        mock_gpio.fire_event(2, mock_gpio.FALLING)
        mock_gpio.fire_event(2, mock_gpio.FALLING)
        mock_gpio.fire_event(2, mock_gpio.FALLING)
        time.sleep(0.5)

    assert len(events) == 4
    assert len(events) == 4
    assert events[0] == {'gpio_pin': 2, 'event': 'rising'}
    assert events[1] == {'gpio_pin': 2, 'event': 'falling'}
    assert events[2] == {'gpio_pin': 2, 'event': 'rising'}
    assert events[3] == {'gpio_pin': 2, 'event': 'falling'}


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
    assert events[0] == {'gpio_pin': 2, 'event': 'motion_on'}
    assert events[1] == {'gpio_pin': 2, 'event': 'motion_off'}
    assert events[2] == {'gpio_pin': 2, 'event': 'motion_on'}
    assert events[3] == {'gpio_pin': 2, 'event': 'motion_off'}


def test_gpio_pull_with_multiple_callbacks_on_pin(mock_gpio):
    dut = gpio.Watcher(["2:motion(1s)", "2:rising", "2:switch"], name='pytest')

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)
        mock_gpio.fire_event(2, mock_gpio.RISING)
        time.sleep(0.1)
        mock_gpio.fire_event(2, mock_gpio.RISING)
        time.sleep(1.2)

    assert len(events) == 6
    assert events[0] == {'gpio_pin': 2, 'event': 'motion_on'}
    assert events[1] == {'gpio_pin': 2, 'event': 'rising'}
    assert events[2] == {'gpio_pin': 2, 'event': 'switch'}
    assert events[3] == {'gpio_pin': 2, 'event': 'rising'}
    assert events[4] == {'gpio_pin': 2, 'event': 'switch'}
    assert events[5] == {'gpio_pin': 2, 'event': 'motion_off'}


def test_callback_from_str():
    res = shared.Callback.from_str("2")
    assert isinstance(res, shared.RisingCallback)
    assert res.gpio_pin == 2

    res = shared.Callback.from_str("2", default=shared.CONST_FALLING)
    assert isinstance(res, shared.FallingCallback)
    assert res.gpio_pin == 2

    res = shared.Callback.from_str("2:rising", default=shared.CONST_FALLING)
    assert isinstance(res, shared.RisingCallback)
    assert res.gpio_pin == 2

    res = shared.Callback.from_str("2:falling", default=shared.CONST_RISING)
    assert isinstance(res, shared.FallingCallback)
    assert res.gpio_pin == 2

    res = shared.Callback.from_str("2:switch", default=shared.CONST_RISING)
    assert isinstance(res, shared.SwitchCallback)
    assert res.gpio_pin == 2
    assert res.delay == shared.SwitchCallback.BOUNCE_DEFAULT

    res = shared.Callback.from_str("2:switch(999)", default=shared.CONST_RISING)
    assert isinstance(res, shared.SwitchCallback)
    assert res.gpio_pin == 2
    assert res.delay == 999

    try:
        shared.Callback.from_str("2:switch()", default=shared.CONST_RISING)
    except ValueError:
        pass

    res = shared.Callback.from_str("2:motion", default=shared.CONST_RISING)
    assert isinstance(res, shared.MotionCallback)
    assert res.gpio_pin == 2
    assert res.delay == parse_duration_literal(shared.MotionCallback.DELAY_DEFAULT)

    res = shared.Callback.from_str("2:motion(2m)", default=shared.CONST_RISING)
    assert isinstance(res, shared.MotionCallback)
    assert res.gpio_pin == 2
    assert res.delay == 120

    try:
        shared.Callback.from_str("2:motion()", default=gpio.CONST_RISING)
    except ValueError:
        pass
