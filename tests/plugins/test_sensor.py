import sys
import time
import types

from mock import Mock

from pnp.plugins.pull.sensor import DHT
from tests.plugins.helper import make_runner, start_runner

# Mock the whole Adafruit Module - that one isn't even available on non-arm architectures
module_name = 'Adafruit_DHT'
mock_adafruit = types.ModuleType(module_name)
sys.modules[module_name] = mock_adafruit
mock_adafruit.read_retry = Mock(name=module_name + '.read_retry')
mock_adafruit.DHT11 = Mock(name=module_name + '.DHT11', return_value='dht11')
mock_adafruit.DHT22 = Mock(name=module_name + '.DHT22', return_value='dht22')
mock_adafruit.AM2302 = Mock(name=module_name + '.AM2302', return_value='am2302')


def test_dht_poll_for_smoke():
    mock_adafruit.read_retry.return_value = (57.5, 23.2)  # (humidity, temp)
    dut = DHT(name='pytest', device='dht22', data_gpio=99, interval="1s")

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(5)

    assert len(events) >= 4
    assert all([e['humidity'] == 57.5 and e['temperature'] == 23.2 for e in events])
