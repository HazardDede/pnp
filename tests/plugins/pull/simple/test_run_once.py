import time

import pytest

from pnp.models import PullModel
from pnp.plugins.pull.simple import RunOnce
from tests.dummies.polling import AsyncPollingDummy
from tests.plugins.pull import make_runner, start_runner


@pytest.mark.asyncio
async def test_pull_without_wrapped_poll():
    dut = RunOnce(name='pytest')
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.01)

    assert runner.events == [{}]


@pytest.mark.asyncio
async def test_pull_with_sync_wrapped_poll():
    dut = RunOnce(name='pytest', poll={'plugin': 'tests.dummies.polling.SyncPollingDummy'})
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.01)

    assert runner.events == [42]


@pytest.mark.asyncio
async def test_async_pull_with_async_wrapped_poll():
    dut = RunOnce(name='pytest', poll={'plugin': 'tests.dummies.polling.AsyncPollingDummy'})
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.01)

    assert runner.events == [42]


def test_init_with_no_poll():
    with pytest.raises(TypeError, match=r"Pull does not support pull_now\(\).*"):
        RunOnce(name='pytest', poll={'plugin': 'tests.dummies.polling.NoPollingDummy'})


def test_repr():
    dut = RunOnce(name='pytest', poll={'plugin': 'tests.dummies.polling.AsyncPollingDummy'})
    expected = repr(PullModel(instance=AsyncPollingDummy(name="pytest_pull")))
    assert repr(dut) == f"RunOnce(model={expected}, name='pytest')"
