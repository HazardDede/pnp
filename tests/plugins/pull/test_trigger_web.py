import socket
import time

import pytest
import requests

from pnp.plugins.pull import trigger, PullBase
from pnp.plugins.pull import AsyncPolling, Polling

from . import make_runner, start_runner


class DummyPoll(Polling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def poll(self):
        return 42


class AsyncDummyPoll(AsyncPolling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def async_poll(self):
        return 42


class ErrorneousDummyPoll(Polling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def poll(self):
        raise Exception("Crash on purpose!")


class NonPollingDummy(PullBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def poll(self):
        raise Exception("Do not call me!")


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


def test_init_endpoint():
    free_port = get_free_tcp_port()
    wrapped = {'plugin': 'tests.plugins.pull.test_trigger_web.DummyPoll'}
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
    wrapped = {'plugin': 'tests.plugins.pull.test_trigger_web.NonPollingDummy'}
    with pytest.raises(TypeError) as tex:
        trigger.Web(name='pytest', port=free_port, poll=wrapped)

    assert "The component to wrap has to be a polling component" in str(tex)


@pytest.mark.parametrize("wrapped", [
    {'plugin': 'tests.plugins.pull.test_trigger_web.DummyPoll'},
    {'plugin': 'tests.plugins.pull.test_trigger_web.AsyncDummyPoll'}
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
    wrapped = {'plugin': 'tests.plugins.pull.test_trigger_web.ErrorneousDummyPoll'}

    dut = trigger.Web(name='pytest', port=free_port, poll=wrapped)
    runner = make_runner(dut, lambda: None)
    with start_runner(runner):
        time.sleep(2)
        response = requests.get('http://localhost:{port}/trigger'.format(port=free_port))
        assert response.status_code == 500
        assert response.json() == {'success': False, 'error': "Crash on purpose!"}
