import pytest

from pnp.plugins.pull import simple
from tests.plugins.pull import CallbackMemory


@pytest.mark.asyncio
async def test_poll():
    dut = simple.Cron(expressions='*/1 * * * * every minute', name='pytest')
    memory = CallbackMemory().bind(dut)

    await dut.poll()
    await dut.poll()
    await dut.poll()

    assert len(memory.events) == 3
    assert all([item == "every minute" for item in memory.events])


def test_repr():
    dut = simple.Cron(expressions='*/1 * * * * every minute', name='pytest')
    assert repr(dut) == "Cron(expressions=['*/1 * * * * every minute'], interval=60, is_cron=False, name='pytest')"