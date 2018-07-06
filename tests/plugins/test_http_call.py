import pytest
import requests

from pnp.plugins.push import PushExecutionError
from pnp.plugins.push.http import Call


def http_call(mp, call_method='GET', call_url='http://localhost:1234/foo/bar', call_data='payload',
              response_data="data", status_code=200, call_assert_fun=None, **kwargs):
    class ResponseMock:
        @property
        def status_code(self):
            return status_code

        @property
        def text(self):
            return ""

        def json(self):
            return response_data

    def call_validator(method, url, data=None):
        if call_assert_fun is None:
            assert method == call_method
            assert url == call_url
            assert data == call_data
        else:
            call_assert_fun(method=method, url=url, data=data)

        return ResponseMock()

    mp.setattr(requests, 'request', call_validator)
    dut = Call(name='pytest', url=call_url, method=call_method, **kwargs)

    return dut.push(call_data)


def test_http_call_push(monkeypatch):
    res = http_call(monkeypatch, call_data="payload")
    assert res == 'payload'  # Payload as is


def test_http_call_on_error(monkeypatch):
    res = http_call(monkeypatch, call_data='payload', status_code=500)
    assert res == 'payload'  # Default fail_on_error = False => payload as is

    with pytest.raises(PushExecutionError) as pe:
        http_call(monkeypatch, call_method='POST', call_url='http://any_host:3546/foo/bar', status_code=500,
                  fail_on_error=True)
    assert "POST of 'http://any_host:3546/foo/bar' failed with status code = '500'" in str(pe)


def test_http_call_provide_response(monkeypatch):
    res = http_call(monkeypatch, response_data=dict(key="value"), provide_response=True)
    assert res == dict(status_code=200, data=dict(key="value"), is_json=True)


def test_http_call_envelope_override(monkeypatch):
    def assert_put_method(**kwargs):
        assert kwargs.pop('method') == "PUT"
        assert kwargs.pop('data') == "payload"
    res = http_call(monkeypatch, call_data=dict(data="payload", method="PUT"), call_assert_fun=assert_put_method)
    assert res == dict(data="payload", method="PUT")

    def assert_url(**kwargs):
        assert kwargs.pop('url') == "http://another_host:9876/bar/baz"
        assert kwargs.pop('data') == "payload"
    res = http_call(monkeypatch, call_data=dict(data="payload", url="http://another_host:9876/bar/baz"),
                    call_assert_fun=assert_url)
    assert res == dict(data="payload", url="http://another_host:9876/bar/baz")

    def assert_fail_on_error(**kwargs):
        assert kwargs.pop('data') == "payload"
    with pytest.raises(PushExecutionError) as pe:
        http_call(monkeypatch, call_data=dict(data="payload", fail_on_error=True), status_code=500,
                  call_assert_fun=assert_fail_on_error)
    assert "GET of 'http://localhost:1234/foo/bar' failed with status code = '500'" in str(pe)
