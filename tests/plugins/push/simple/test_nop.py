import pytest

from pnp.plugins.push.simple.nop import Nop


@pytest.mark.asyncio
async def test_push():
    dut = Nop(name="pytest")
    assert await dut.push("unaltered") == "unaltered"
    assert await dut.push({"data": "value"}) == {"data": "value"}
    assert await dut.push({"data": "value", "k1": "v1"}) == {"data": "value", "k1": "v1"}


def test_repr():
    dut = Nop(name="pytest")
    assert repr(dut) == "Nop(name='pytest')"
