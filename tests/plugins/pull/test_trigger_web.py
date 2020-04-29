import socket
import time

import pytest
import requests

from pnp.plugins.pull import trigger
from . import make_runner, start_runner


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


def test_init_endpoint():
    free_port = get_free_tcp_port()
    wrapped = {'plugin': 'tests.dummies.polling.SyncPollingDummy'}
    dut = trigger.Web(name='pytest', port=free_port, poll=wrapped)
    assert dut.endpoint == '/trigger'
    dut = trigger.Web(name='pytest', port=free_port, poll=wrapped, endpoint='trigger')
    assert dut.endpoint == '/trigger'
    dut = trigger.Web(name='pytest', port=free_port, poll=wrapped, endpoint='')
    assert dut.endpoint == '/'
    dut = trigger.Web(name='pytest', port=free_port, poll=wrapped, endpoint=None)
    assert dut.endpoint == '/'
    dut = trigger.Web(name='pytest', port=free_port, poll=wrapped, endpoint='/foo')
    assert dut.endpoint == '/foo'


def test_init_non_polling_pull():
    free_port = get_free_tcp_port()
    wrapped = {'plugin': 'tests.dummies.polling.NoPollingDummy'}
    with pytest.raises(TypeError) as tex:
        trigger.Web(name='pytest', port=free_port, poll=wrapped)

    assert "The component to wrap has to be a polling component" in str(tex)


@pytest.mark.parametrize("wrapped", [
    {'plugin': 'tests.dummies.polling.SyncPollingDummy'},
    {'plugin': 'tests.dummies.polling.AsyncPollingDummy'}
])
def test_pull(wrapped):
    events = []
    def callback(plugin, payload):
        events.append(payload)

    free_port = get_free_tcp_port()

    dut = trigger.Web(name='pytest', port=free_port, poll=wrapped)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(2)
        response = requests.get('http://localhost:{port}/trigger'.format(port=free_port))
        assert response.status_code == 200
        assert response.json() == {'success': True, 'payload': 42}
        response = requests.get('http://localhost:{port}/trigger'.format(port=free_port))
        assert response.json() == {'success': True, 'payload': 42}
        response = requests.get('http://localhost:{port}/trigger'.format(port=free_port))
        assert response.json() == {'success': True, 'payload': 42}
        time.sleep(0.1)

    assert events == [42, 42, 42]


def test_pull_for_error():
    free_port = get_free_tcp_port()
    wrapped = {'plugin': 'tests.dummies.polling.ErrorPollingDummy'}

    dut = trigger.Web(name='pytest', port=free_port, poll=wrapped)
    runner = make_runner(dut, lambda: None)
    with start_runner(runner):
        time.sleep(2)
        response = requests.get('http://localhost:{port}/trigger'.format(port=free_port))
        assert response.status_code == 500
        assert response.json() == {'success': False, 'error': "Crash on purpose!"}
