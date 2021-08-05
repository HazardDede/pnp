import time

import pytest

from pnp.plugins.pull.simple import Repeat
from tests.plugins.pull import make_runner, start_runner


@pytest.mark.asyncio
async def test_pull():
    dut = Repeat(name='pytest', repeat="Hello World", interval=0.001)
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.01)

    assert len(runner.events) >= 6
    assert all([p == "Hello World" for p in runner.events])


def test_wait_compat():
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


def test_repr():
    dut = Repeat(name='pytest', repeat="Hello World", interval=0.001)
    assert repr(dut) == "Repeat(interval=0.001, name='pytest', repeat='Hello World')"
