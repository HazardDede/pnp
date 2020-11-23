import pytest

from pnp.plugins.pull import simple


@pytest.mark.asyncio
async def test_cron_every_minute():
    res = list()
    def on_payload(sender, payload):
        res.append(payload)

    dut = simple.Cron(expressions='*/1 * * * * every minute', name='pytest')
    dut.callback(on_payload)

    await dut.poll()
    await dut.poll()
    await dut.poll()

    assert len(res) == 3
    assert res[0] == 'every minute'
