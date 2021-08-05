import time

import pytest

from pnp.plugins.pull.fitbit import Current
from tests.plugins.pull import make_runner, start_runner


@pytest.mark.asyncio
async def test_poll_for_smoke(token_file, mocker):
    fb_mock = mocker.patch('fitbit.Fitbit')
    fb_mock.return_value.time_series.return_value = {"steps": [{'value': '1000'}, {'value': '2000'}, {'value': '3000'}]}

    dut = Current(
        resources=['activities/steps', 'activities/distance'],
        config=token_file, name='pytest',
        instant_run=True
    )
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.5)

    events = runner.events
    assert len(events) >= 1
    assert events[0] == {'activities/steps': 3000, 'activities/distance': 3000.0}


def test_repr(token_file):
    dut = Current(
        resources=['activities/steps', 'activities/distance'],
        config=token_file, name='pytest',
        instant_run=True
    )
    assert repr(dut) == (
        f"Current(config='{token_file}', interval=60, is_cron=False, name='pytest', "
        f"resources=['activities/steps', 'activities/distance'], system=None)"
    )
