from functools import partial

import pytest

from pnp.plugins.push import simple

DUT = partial(simple.Wait, name='pytest')


def test_init():
    dut = DUT(10)
    assert isinstance(dut.waiting_interval, float)
    assert dut.waiting_interval == 10.0

    dut = DUT(0.9)
    assert isinstance(dut.waiting_interval, float)
    assert dut.waiting_interval == 0.9

    dut = DUT('1m')
    assert isinstance(dut.waiting_interval, float)
    assert dut.waiting_interval == 60.0


@pytest.mark.asyncio
async def test_async_push_for_smoke():
    dut = DUT(0.01)
    assert await dut.push("TEST") == "TEST"
