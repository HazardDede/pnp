import time

import pytest

from pnp.plugins.pull.simple import RunOnce
from . import make_runner, start_runner


def test_init_with_no_poll():
    with pytest.raises(TypeError, match=r"Pull does not support pull_now\(\) / async_pull_now\(\).*"):
        RunOnce(name='pytest', poll={'plugin': 'tests.dummies.polling.NoPollingDummy'})


def test_pull_without_wrapped_poll():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = RunOnce(name='pytest')
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.01)

    assert events == [{}]


@pytest.mark.asyncio
async def test_async_pull_without_wrapped_poll():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = RunOnce(name='pytest')
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.01)

    assert events == [{}]


@pytest.mark.asyncio
async def test_async_pull_with_sync_wrapped_poll():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = RunOnce(name='pytest', poll={'plugin': 'tests.dummies.polling.SyncPollingDummy'})
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.01)

    assert events == [42]


@pytest.mark.asyncio
async def test_async_pull_with_async_wrapped_poll():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = RunOnce(name='pytest', poll={'plugin': 'tests.dummies.polling.AsyncPollingDummy'})
    dut.on_payload = callback
    await dut.async_pull()

    assert events == [42]
