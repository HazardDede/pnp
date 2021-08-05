import pytest

from pnp.plugins.push.simple.echo import Echo


@pytest.mark.asyncio
async def test_push():
    dut = Echo(name="pytest")
    assert await dut.push("Push me") == "Push me"
    assert await dut.push({"data": "Push me"}) == "Push me"
    assert await dut.push({"data": "Push me", "k1": "v1"}) == {"payload": "Push me", "k1": "v1"}


def test_repr():
    dut = Echo(name="pytest")
    assert repr(dut) == "Echo(name='pytest')"
