import json
import socket
import time

import requests

from pnp.plugins.pull.http import Server
from tests.plugins.helper import make_runner, start_runner


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


def _run_test(url, data, assertion_fun, method=requests.get, allowed_methods='GET', status_code=200,
              server_impl='gevent'):
    output = None
    def callback(plugin, payload):
        nonlocal output
        output = payload

    port = get_free_tcp_port()
    dut = Server(port=port, name='pytest', allowed_methods=allowed_methods, server_impl=server_impl)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)
        kwargs = dict(url=url.format(port=port))
        if data is not None:
            kwargs['data'] = data
        resp = method(**kwargs)

    assert resp.status_code == status_code
    assertion_fun(output)


def test_http_server_json_data():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint"
        assert payload['method'] == "GET"
        assert payload['query'] == {'foo': 'bar', 'bar': 'baz'}
        assert payload['data'] == {"baz": "bar"}
        assert payload['is_json'] is True

    _run_test(
        url='http://localhost:{port}/resource/endpoint?foo=bar&bar=baz',
        data=json.dumps({"baz": "bar"}),
        assertion_fun=assert_this
    )


def test_http_server_json_data_flask_server():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint"
        assert payload['method'] == "GET"
        assert payload['query'] == {'foo': 'bar', 'bar': 'baz'}
        assert payload['data'] == {"baz": "bar"}
        assert payload['is_json'] is True

    _run_test(
        url='http://localhost:{port}/resource/endpoint?foo=bar&bar=baz',
        data=json.dumps({"baz": "bar"}),
        assertion_fun=assert_this,
        server_impl='flask'
    )


def test_http_server_non_json_data():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint"
        assert payload['method'] == "GET"
        assert payload['query'] == {'foo': 'bar', 'bar': 'baz'}
        assert payload['data'] == b'foobarbaznojson'
        assert payload['is_json'] is False

    _run_test(
        url='http://localhost:{port}/resource/endpoint?foo=bar&bar=baz',
        data="foobarbaznojson",
        assertion_fun=assert_this
    )


def test_http_server_multiple_query_params():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint/queryparam"
        assert payload['method'] == "GET"
        assert payload['query'] == {'foo': 'bar', 'bar': ['baz', 'foo']}
        assert payload['data'] is None
        assert payload['is_json'] is False

    _run_test(
        url='http://localhost:{port}/resource/endpoint/queryparam?foo=bar&bar=baz&bar=foo',
        data=None,
        assertion_fun=assert_this
    )


def test_http_server_query_params_wo_value():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint/queryparam"
        assert payload['method'] == "GET"
        assert payload['query'] == {'foo': None, 'bar': [None, None]}
        assert payload['data'] is None
        assert payload['is_json'] is False

    _run_test(
        url='http://localhost:{port}/resource/endpoint/queryparam?foo=&bar=&bar',
        data=None,
        assertion_fun=assert_this
    )


def test_http_server_query_different_methods():
    def assert_this(payload):
        assert payload['method'] == 'GET'
    _run_test(
        url='http://localhost:{port}/resource/endpoint/queryparam?foo=&bar=&bar',
        data=None,
        assertion_fun=assert_this
    )

    def assert_this(payload):
        assert payload['method'] == 'POST'
    _run_test(
        url='http://localhost:{port}/resource/endpoint/queryparam?foo=&bar=&bar',
        data=None,
        allowed_methods='POST',
        method=requests.post,
        assertion_fun=assert_this
    )

    def assert_this(payload):
        assert payload is None
    _run_test(
        url='http://localhost:{port}/resource/endpoint/queryparam?foo=&bar=&bar',
        data=None,
        allowed_methods='GET',
        method=requests.post,
        assertion_fun=assert_this,
        status_code=405
    )
