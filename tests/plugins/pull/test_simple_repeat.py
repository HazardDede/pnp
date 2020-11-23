import time

import pytest

from pnp.plugins.pull.simple import Repeat
from . import make_runner, start_runner


@pytest.mark.asyncio
async def test_repeat_pull():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = Repeat(name='pytest', repeat="Hello World", wait=0.001)
    runner = await make_runner(dut, callback)
    async with start_runner(runner):
        time.sleep(0.01)

    assert len(events) >= 2
    assert all([p == "Hello World" for p in events])


def test_repeat_wait_compat():
    dut = Repeat(name='pytest', wait=0.5, repeat="Hello World")
    assert dut.interval == 0.5
    dut = Repeat(name='pytest', wait="1m", repeat="Hello World")
    assert dut.interval == 60
    dut = Repeat(name='pytest', interval="1m", repeat="Hello World")
    assert dut.interval == 60
    dut = Repeat(name='pytest', wait="2m", interval="1m", repeat="Hello World")
    assert dut.interval == 60
    dut = Repeat(name='pytest', repeat="Hello World")
    assert dut.interval == 5
