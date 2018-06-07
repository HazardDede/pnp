import pytest
import requests

from pnp.plugins.pull import PollingError
from pnp.plugins.pull.zway import ZwayPoll


class ZwayResponseDummy:
    @property
    def status_code(self):
        return 200

    @property
    def text(self):
        return ""

    def json(self):
        return {}


def test_zway_poll(monkeypatch):
    zway_url = 'http://test:8083/ZWaveAPI/Run/devices'
    zway_user = 'admin'
    zway_password = 'secret'

    def call_validator(url, auth):
        assert url == zway_url
        assert auth.username == zway_user
        assert auth.password == zway_password

        return ZwayResponseDummy()

    monkeypatch.setattr(requests, 'get', call_validator)

    dut = ZwayPoll(name='pytest', url=zway_url, user=zway_user, password=zway_password)

    assert dut.poll() == {}


def test_zway_poll_on_error(monkeypatch):
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
    dut = ZwayPoll(name='pytest', url=zway_url, user=zway_user, password=zway_password)
    with pytest.raises(PollingError):
        dut.poll()
