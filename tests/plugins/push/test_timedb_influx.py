from box import Box
from mock import patch

from pnp.plugins.push.timedb import InfluxPush


@patch('influxdb.InfluxDBClient')
def test_influx_push(mock_influx_db_client):
    mc = mock_influx_db_client.return_value

    dut = InfluxPush(name='pytest', host='localhost', port=1234, user='user', password='secret',
                     database='testdb', protocol="{payload.a}, {payload.b}")
    dut.push(Box(dict(a="foo", b="bar", c="baz")))

    mock_influx_db_client.assert_called
    mc.write.assert_called
    mc.write.assert_called_with(['foo, bar'], {'db': 'testdb'}, 204, 'line')
