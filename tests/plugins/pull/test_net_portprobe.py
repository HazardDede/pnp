from mock import patch

from pnp.plugins.pull.net import PortProbe


@patch("pnp.plugins.pull.net.socket")
def test_port_probe_remote(socket_mock):
    socket_mock.socket.return_value.__enter__.return_value.connect_ex.return_value = 0

    dut = PortProbe(9999, 'www.anyserver.de', name='pytest')
    payload = dut.poll()
    assert payload == {
        PortProbe.CONST_SERVER: 'www.anyserver.de',
        PortProbe.CONST_PORT: 9999,
        PortProbe.CONST_REACHABLE: True
    }

    socket_mock.socket.return_value.__enter__.return_value.connect_ex.return_value = 255
    payload = dut.poll()
    assert payload == {
        PortProbe.CONST_SERVER: 'www.anyserver.de',
        PortProbe.CONST_PORT: 9999,
        PortProbe.CONST_REACHABLE: False
    }


@patch("pnp.plugins.pull.net.socket")
def test_port_probe_remote(socket_mock):
    dut = PortProbe(9999, 'localhost', name='pytest')
    payload = dut.poll()
    assert payload == {
        PortProbe.CONST_SERVER: 'localhost',
        PortProbe.CONST_PORT: 9999,
        PortProbe.CONST_REACHABLE: False
    }

    assert socket_mock.socket.return_value.__enter__.return_value.listen.call_count == 2
