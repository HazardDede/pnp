import math
import sys
import types

import pytest
from mock import Mock

from pnp.plugins.pull.sensor import DHT

# Mock the whole Adafruit Module - that one isn't even available on non-arm architectures
module_name = 'Adafruit_DHT'
mock_adafruit = types.ModuleType(module_name)
sys.modules[module_name] = mock_adafruit
mock_adafruit.read_retry = Mock(name=module_name + '.read_retry')
mock_adafruit.DHT11 = Mock(name=module_name + '.DHT11', return_value='dht11')
mock_adafruit.DHT22 = Mock(name=module_name + '.DHT22', return_value='dht22')
mock_adafruit.AM2302 = Mock(name=module_name + '.AM2302', return_value='am2302')


@pytest.mark.asyncio
async def test_poll_for_smoke():
    mock_adafruit.read_retry.return_value = (57.5, 23.2)  # (humidity, temp)
    dut = DHT(name='pytest', device='dht22', data_gpio=99, interval="1s")

    res = await dut.poll()

    assert all([math.isclose(e['humidity'], 57.5) and math.isclose(e['temperature'], 23.2) for e in [res]])


@pytest.mark.asyncio
async def test_poll_with_offset():
    mock_adafruit.read_retry.return_value = (57.5, 23.2)  # (humidity, temp)
    dut = DHT(name='pytest', device='dht22', data_gpio=99, interval="1s", humidity_offset=-5.25, temp_offset=1.5)

    res = await dut.poll()

    assert all([math.isclose(e['humidity'], 52.25) and math.isclose(e['temperature'], 24.7) for e in [res]])


def test_repr():
    dut = DHT(name='pytest', device='dht22', data_gpio=99, interval="1s", humidity_offset=-5.25, temp_offset=1.5)
    assert repr(dut) == (
        "DHT(data_gpio=99, device='dht22', humidity_offset=-5.25, interval='1s', "
        "is_cron=False, name='pytest', temp_offset=1.5)"
    )
