import json

import pytest

from pnp.plugins.push.hass import Service

HASS_URL = 'http://hass:8123'
HA_TOKEN = 'abcdefg'
DOMAIN = "frontend"
SERVICE = "set_theme"
DATA = {"name": "clear"}
TIMEOUT = 10


class HassResponseDummy:
    def __init__(self, status_code=200):
        self._status_code = int(status_code)

    @property
    def status_code(self):
        return self._status_code

    @property
    def text(self):
        import json
        return json.dumps(self.json())

    def json(self):
        if self.status_code == 200:
            return {}
        raise RuntimeError("Accessing json() is prohibited when status_code <> 200")


@pytest.mark.asyncio
async def test_push_with_valid_call(monkeypatch):
    called = False

    def call_validator(url, *args, headers=None, timeout=None, data=None, **kwargs):
        assert url == "{hass_url}/api/services/{domain}/{service}".format(
            hass_url=HASS_URL, domain=DOMAIN, service=SERVICE)
        assert headers == {
            'Authorization': 'Bearer {token}'.format(token=HA_TOKEN),
            'content-type': 'application/json',
        }
        assert timeout == TIMEOUT
        assert data == json.dumps(DATA)
        nonlocal called
        called = True
        return HassResponseDummy()

    import requests
    monkeypatch.setattr(requests, 'post', call_validator)

    dut = Service(name='pytest', url=HASS_URL, token=HA_TOKEN, timeout=TIMEOUT, domain=DOMAIN, service=SERVICE)

    await dut.push(DATA)
    assert called


@pytest.mark.asyncio
async def test_push_with_errornous_call(monkeypatch):
    def call_validator(*args, **kwargs):
        return HassResponseDummy(402)

    import requests
    monkeypatch.setattr(requests, 'post', call_validator)

    dut = Service(name='pytest', url=HASS_URL, token=HA_TOKEN, timeout=TIMEOUT, domain=DOMAIN, service=SERVICE)

    with pytest.raises(
            RuntimeError,
            match="Failed to call the service services/frontend/set_theme @ http://hass:8123"
    ):
        await dut.push(DATA)
