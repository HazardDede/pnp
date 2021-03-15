import time

import pytest

from pnp.plugins.pull.fitbit import Devices
from tests.plugins.pull import make_runner, start_runner


@pytest.mark.asyncio
async def test_poll_for_smoke(token_file, mocker):

    fb_mock = mocker.patch('fitbit.Fitbit')
    fb_mock.return_value.get_devices.return_value = [{
        'battery': 'Empty',
        'batteryLevel': 10,
        'deviceVersion': 'Charge 2',
        'features': [],
        'id': 'abc',
        'lastSyncTime': '2018-12-23T10:47:40.000',
        'mac': 'AAAAAAAAAAAA',
        'type': 'TRACKER'
    }, {
        'battery': 'High',
        'batteryLevel': 95,
        'deviceVersion': 'Blaze',
        'features': [],
        'id': 'xyz',
        'lastSyncTime': '2019-01-02T10:48:39.000',
        'mac': 'FFFFFFFFFFFF',
        'type': 'TRACKER'
    }]

    dut = Devices(config=token_file, name='pytest', instant_run=True)
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.5)

    events = runner.events
    assert len(events) >= 1
    assert events[0] == [{
        'battery': 'Empty',
        'battery_level': 10,
        'device_version': 'Charge 2',
        'features': [],
        'id': 'abc',
        'last_sync_time': '2018-12-23T10:47:40.000',
        'mac': 'AAAAAAAAAAAA',
        'type': 'TRACKER'
    }, {
        'battery': 'High',
        'battery_level': 95,
        'device_version': 'Blaze',
        'features': [],
        'id': 'xyz',
        'last_sync_time': '2019-01-02T10:48:39.000',
        'mac': 'FFFFFFFFFFFF',
        'type': 'TRACKER'
    }]


def test_repr(token_file):
    dut = Devices(config=token_file, name='pytest', instant_run=True)
    assert repr(dut) == (
        f"Devices(config='{token_file}', interval=60, is_cron=False, name='pytest', system=None)"
    )
