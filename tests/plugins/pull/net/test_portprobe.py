import socket

from pnp.plugins.pull.net import PortProbe


def test_poll_remote(mocker):
    socket_mock = mocker.patch("pnp.plugins.pull.net.portprobe.socket")
    socket_mock.socket.return_value.__enter__.return_value.connect_ex.return_value = 0

    dut = PortProbe(9999, 'www.anyserver.de', name='pytest')
    payload = dut._poll()
    assert payload == {
        'server': 'www.anyserver.de',
        'port': 9999,
        'reachable': True
    }

    socket_mock.socket.return_value.__enter__.return_value.connect_ex.return_value = 255
    payload = dut._poll()
    assert payload == {
        'server': 'www.anyserver.de',
        'port': 9999,
        'reachable': False
    }


def test_poll_local(mocker):
    socket_mock = mocker.patch("pnp.plugins.pull.net.portprobe.socket")

    dut = PortProbe(9999, 'localhost', name='pytest')
    payload = dut._poll()
    assert payload == {
        'server': 'localhost',
        'port': 9999,
        'reachable': False
    }
    assert socket_mock.socket.return_value.__enter__.return_value.listen.call_count == 2

    socket_mock.error = OSError
    socket_mock.socket.return_value.__enter__.return_value.bind.side_effect = socket.error('Failed on purpose')
    payload = dut._poll()
    assert payload == {
        'server': 'localhost',
        'port': 9999,
        'reachable': True
    }
    assert socket_mock.socket.return_value.__enter__.return_value.listen.call_count == 2  # No change


def test_repr():
    dut = dut = PortProbe(9999, 'localhost', name='pytest')
    assert repr(dut) == "PortProbe(interval=60, is_cron=False, name='pytest', port=9999, server='localhost', timeout=1)"
