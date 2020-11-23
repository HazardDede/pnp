import time
from datetime import datetime

import pytest

from pnp.plugins.pull import StopPollingError
from pnp.plugins.pull.simple import CustomPolling
from . import make_runner, start_runner


@pytest.mark.asyncio
async def test_poll():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    def poll():
        return datetime.now()

    dut = CustomPolling(name='pytest', interval="1s", scheduled_callable=poll)
    assert not dut.is_cron
    assert dut._poll_interval == 1
    runner = await make_runner(dut, callback)
    async with start_runner(runner):
        time.sleep(3)

    assert len(events) >= 2


@pytest.mark.asyncio
async def test_poll_for_aborting():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    def poll():
        raise StopPollingError()

    runner = await make_runner(CustomPolling(name='pytest', interval="1s", scheduled_callable=poll), callback)
    async with start_runner(runner):
        time.sleep(1)

    assert len(events) == 0


def test_poll_with_cron_expression():
    from cronex import CronExpression

    def poll():
        pass

    dut = CustomPolling(name='pytest', interval="*/1 * * * *", scheduled_callable=poll)
    assert dut.is_cron
    assert isinstance(dut._cron_interval, CronExpression)
    assert dut._cron_interval.string_tab == ['*/1', '*', '*', '*', '*']
