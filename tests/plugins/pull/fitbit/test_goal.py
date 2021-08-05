import time

import pytest

from pnp.plugins.pull.fitbit import Goal
from tests.plugins.pull import make_runner, start_runner


@pytest.mark.asyncio
async def test_poll_for_smoke(token_file, mocker):
    fb_mock = mocker.patch('fitbit.Fitbit')
    fb_mock.return_value.activities_daily_goal.return_value = {"goals": {'steps': 3000}}
    fb_mock.return_value.activities_weekly_goal.return_value = {"goals": {'steps': 6000}}
    fb_mock.return_value.body_fat_goal.return_value = {"goal": {"fat": 15.5}}

    dut = Goal(
        goals=['activities/daily/steps', 'activities/weekly/steps', 'body/fat'],
        config=token_file, name='pytest',
        instant_run=True
    )
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.5)

    events = runner.events
    assert len(events) >= 1
    assert events[0] == {'activities/daily/steps': 3000, 'activities/weekly/steps': 6000, 'body/fat': 15.5}


def test_repr(token_file):
    dut = Goal(
        goals=['activities/daily/steps', 'activities/weekly/steps', 'body/fat'],
        config=token_file, name='pytest',
        instant_run=True
    )
    assert repr(dut) == (
        f"Goal(config='{token_file}', goals=['activities/daily/steps', 'activities/weekly/steps', 'body/fat'], "
        f"interval=60, is_cron=False, name='pytest', system=None)"
    )
