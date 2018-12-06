import time

import math
from mock import patch, mock_open

from pnp.plugins.pull.monitor import Stats

from .helper import start_runner, make_runner


def configure_mocks(mock_psutil, mock_os):
    mock_psutil.cpu_count.return_value = 8
    mock_psutil.cpu_freq.return_value.current = 700
    mock_psutil.cpu_percent.return_value = 56.7
    mock_psutil.disk_usage.return_value.percent = 42.2
    mock_psutil.virtual_memory.return_value.percent = 33.3
    mock_psutil.swap_memory.return_value.percent = 66.7
    mock_psutil.disk_usage.return_value.percent = 42.2

    mock_os.getloadavg.return_value = (0.5, 0.75, 1.0)


@patch("pnp.plugins.pull.monitor.psutil")
@patch("pnp.plugins.pull.monitor.os")
def test_stats_pull_for_smoke(mock_os, mock_psutil):
    configure_mocks(mock_psutil, mock_os)

    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = Stats(name='pytest', instant_run=True)
    runner = make_runner(dut, callback)
    with patch("builtins.open", mock_open(read_data="48200.0")) as mock_file:
        with start_runner(runner):
            time.sleep(0.5)
        mock_file.assert_called_with("/sys/class/thermal/thermal_zone0/temp")

    assert len(events) >= 1
    evt = events[0]
    assert evt['cpu_count'] == 8
    assert evt['cpu_freq'] == 700
    assert math.isclose(evt['cpu_use'], 56.7)
    assert math.isclose(evt['cpu_temp'], 48.2)
    assert math.isclose(evt['memory_use'], 33.3)
    assert math.isclose(evt['swap_use'], 66.7)
    assert math.isclose(evt['disk_use'], 42.2)
    assert math.isclose(evt['load_1m'], 0.5)
    assert math.isclose(evt['load_5m'], 0.75)
    assert math.isclose(evt['load_15m'], 1.0)
