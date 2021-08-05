import pytest
from box import Box

from pnp.plugins.push.storage import Influx


@pytest.mark.asyncio
async def test_push(mocker):
    mock_influx_db_client = mocker.patch('pnp.plugins.push.storage.influx.InfluxDBClient')
    mc = mock_influx_db_client.return_value

    dut = Influx(name='pytest', host='localhost', port=1234, user='user', password='secret',
                     database='testdb', protocol="{payload.a}, {payload.b}")
    await dut.push(Box(dict(a="foo", b="bar", c="baz")))

    mock_influx_db_client.assert_called
    mc.write.assert_called
    mc.write.assert_called_with(['foo, bar'], {'db': 'testdb'}, 204, 'line')


def test_repr():
    dut = Influx(name='pytest', host='localhost', port=1234, user='user', password='secret',
                     database='testdb', protocol="{payload.a}, {payload.b}")
    assert repr(dut) == "Influx(database='testdb', host='localhost', name='pytest', port=1234, " \
                        "protocol='{payload.a}, {payload.b}', user='user')"


def test_backwards_compat():
    from pnp.plugins.push.timedb import InfluxPush
    _ = InfluxPush
