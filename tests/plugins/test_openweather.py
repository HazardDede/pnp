import json
import time

import pytest
import requests

from pnp.plugins.pull.sensor import OpenWeather
from .helper import make_runner, start_runner


VALID_RESPONSE = '{"coord":{"lon":9.65,"lat":53.75},"weather":[{"id":802,"main":"Clouds","description":"Überwiegend bewölkt","icon":"03d"}],"base":"stations","main":{"temp":13,"pressure":1018,"humidity":58,"temp_min":13,"temp_max":13},"visibility":10000,"wind":{"speed":10.3,"deg":320},"clouds":{"all":40},"dt":1538560200,"sys":{"type":1,"id":4883,"message":0.0027,"country":"DE","sunrise":1538544435,"sunset":1538585543},"id":2930821,"name":"Elmshorn","cod":200}'


def patch_requests_for_openweather(monkeypatch, status_code, response):
    class ResponseMock:
        @property
        def status_code(self):
            return status_code

        @property
        def text(self):
            return ""

        def json(self):
            return response

    def call_validator(url):
        return ResponseMock()

    monkeypatch.setattr(requests, 'get', call_validator)


def test_openweather_for_valid_response(monkeypatch):
    response = json.loads(VALID_RESPONSE)

    patch_requests_for_openweather(monkeypatch, 200, response)

    dut = OpenWeather(name='pytest', api_key="secret", city_name="Elmshorn", interval="1s", instant_run=True)

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(1)

    assert len(events) > 0
    assert events[0]['raw'] == response


def test_openweather_lat_lon_city_name():
    # Valid: City only
    OpenWeather(name='pytest', api_key="secret", city_name="Elmshorn")
    # Valid: Lat/Lon
    OpenWeather(name='pytest', api_key="secret", lat=1.0, lon=1.0)
    # Invalid: None
    with pytest.raises(ValueError) as ve:
        OpenWeather(name='pytest', api_key="secret")
    assert "You have to pass city_name or lat and lon." in str(ve)
    # Invalid: lat without lon
    with pytest.raises(ValueError) as ve:
        OpenWeather(name='pytest', api_key="secret", lat=1.0)
    assert "You have to pass city_name or lat and lon." in str(ve)
    # Invalid: lon without lat
    with pytest.raises(ValueError) as ve:
        OpenWeather(name='pytest', api_key="secret", lon=1.0)
    assert "You have to pass city_name or lat and lon." in str(ve)


def test_openweather_tz_for_smoke():
    OpenWeather(name='pytest', api_key="secret", city_name="Elmshorn")  # local timezone
    OpenWeather(name='pytest', api_key="secret", city_name="Elmshorn", tz="GMT")  # tz override with GMT