import pytest

from pnp.plugins.udf.hass import State


HASS_URL = 'http://hass:8123'
HA_TOKEN = 'abcdefg'
ENTITY_ID = "sun.sun"
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
            return {'state': 'below_horizon', 'attributes': {'azimuth': 200}}
        return {'error': 'Entity is unknown'}


def test_hass_state_for_correctness(monkeypatch):
    def call_validator(url, *args, headers=None, timeout=None, **kwargs):
        assert url == "{hass_url}/api/states/{entity_id}".format(hass_url=HASS_URL, entity_id=ENTITY_ID)
        assert headers == {
            'Authorization': 'Bearer {token}'.format(token=HA_TOKEN),
            'content-type': 'application/json',
        }
        assert timeout == timeout

        return HassResponseDummy()

    import requests
    monkeypatch.setattr(requests, 'get', call_validator)

    dut = State(name='pytest', url=HASS_URL, token=HA_TOKEN, timeout=TIMEOUT)

    assert dut.action(ENTITY_ID) == 'below_horizon'
    assert dut.action(ENTITY_ID, attribute='azimuth') == 200


def test_hass_state_for_error(monkeypatch):
    def call_validator(*args, **kwargs):
        return HassResponseDummy(402)

    import requests
    monkeypatch.setattr(requests, 'get', call_validator)

    dut = State(name='pytest', url=HASS_URL, token=HA_TOKEN, timeout=TIMEOUT)

    with pytest.raises(RuntimeError) as e:
        dut.action(ENTITY_ID)
    assert "Failed to fetch the state for sun.sun @ http://hass:8123" in str(e)
