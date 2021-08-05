import pytest
import requests

from pnp.plugins.pull import PollingError
from pnp.plugins.pull.http.zwayfetch import ZwayFetch


class ZwayResponseDummy:
    @property
    def status_code(self):
        return 200

    @property
    def text(self):
        return ""

    def json(self):
        return {}


def test_poll(monkeypatch):
    zway_url = 'http://test:8083/ZWaveAPI/Run/devices'
    zway_user = 'admin'
    zway_password = 'secret'

    def call_validator(url, auth):
        assert url == zway_url
        assert auth.username == zway_user
        assert auth.password == zway_password

        return ZwayResponseDummy()

    monkeypatch.setattr(requests, 'get', call_validator)

    dut = ZwayFetch(name='pytest', url=zway_url, user=zway_user, password=zway_password)

    assert dut._poll() == {}


def test_poll_on_error(monkeypatch):
    zway_url = 'http://test:8083/ZWaveAPI/Run/devices'
    zway_user = 'admin'
    zway_password = 'secret'

    class ZwayResponseError(ZwayResponseDummy):
        @property
        def status_code(self):
            return 500

    def call_validator(url, auth):
        assert url == zway_url
        assert auth.username == zway_user
        assert auth.password == zway_password

        return ZwayResponseError()

    monkeypatch.setattr(requests, 'get', call_validator)
    dut = ZwayFetch(name='pytest', url=zway_url, user=zway_user, password=zway_password)
    with pytest.raises(PollingError):
        dut._poll()


def test_backwards_compat():
    from pnp.plugins.pull.zway import ZwayPoll
    _ = ZwayPoll


def test_repr():
    dut = ZwayFetch(name='pytest', url="http://test:8083/ZWaveAPI/Run/devices", user="admin", password="foo")
    assert repr(dut) == (
        "ZwayFetch(interval=60, is_cron=False, name='pytest', "
        "url='http://test:8083/ZWaveAPI/Run/devices', user='admin')"
    )
