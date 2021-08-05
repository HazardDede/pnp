import time

import pytest

from pnp.plugins.pull.simple import Count
from tests.plugins.pull import make_runner, start_runner


@pytest.mark.asyncio
async def test_pull():
    dut = Count(name='pytest', from_cnt=0, to_cnt=5, wait=0.001)
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.06)

    assert runner.events == [0, 1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_pull_infinity():
    dut = Count(name='pytest', from_cnt=0, to_cnt=None, wait=0.001)
    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.012)

    expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert all([exp == actual for exp, actual in zip(expected, runner.events)])


def test_wait_compat():
    dut = Count(name='pytest', wait=0.5)
    assert dut.interval == 0.5
    dut = Count(name='pytest', wait="1m")
    assert dut.interval == 60
    dut = Count(name='pytest', interval="1m")
    assert dut.interval == 60
    dut = Count(name='pytest', wait="2m", interval="1m")
    assert dut.interval == 60
    dut = Count(name='pytest')
    assert dut.interval == 5


def test_repr():
    dut = Count(name='pytest', wait=0.5, from_cnt=1, to_cnt=10)
    assert repr(dut) == "Count(from_cnt=1, interval=0.5, name='pytest', to_cnt=10)"
