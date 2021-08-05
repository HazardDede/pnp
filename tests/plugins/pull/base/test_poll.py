import time
from datetime import datetime

import pytest

from pnp.plugins.pull import StopPollingError
from tests.plugins.pull import make_runner, start_runner, CustomPolling


@pytest.mark.asyncio
async def test_poll():
    def poll():
        return datetime.now()

    dut = CustomPolling(name='pytest', interval="1s", scheduled_callable=poll)
    assert not dut.is_cron
    assert dut._poll_interval == 1

    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(3)

    assert len(runner.events) >= 2


@pytest.mark.asyncio
async def test_poll_for_aborting():
    def poll():
        raise StopPollingError()

    dut = CustomPolling(name='pytest', interval="1s", scheduled_callable=poll)
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(1)

    assert len(runner.events) == 0


def test_poll_with_cron_expression():
    from cronex import CronExpression

    def poll():
        pass

    dut = CustomPolling(name='pytest', interval="*/1 * * * *", scheduled_callable=poll)
    assert dut.is_cron
    assert isinstance(dut._cron_interval, CronExpression)
    assert dut._cron_interval.string_tab == ['*/1', '*', '*', '*', '*']
