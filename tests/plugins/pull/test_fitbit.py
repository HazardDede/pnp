import os
import tempfile
import time
from ruamel import yaml

import pytest
from mock import patch

from pnp.plugins.pull.fitbit import Current, Goal, Devices
from ..helper import make_runner, start_runner


@pytest.yield_fixture(scope='function')
def token_file():
    tokens = {
        'client_id': '123456',
        'client_secret': 'abcdefg',
        'access_token': 'zyx',
        'refresh_token': 'refresh_token',
        'expires_at': 123.567
    }
    with tempfile.NamedTemporaryFile('w') as tf:
        yaml.dump(tokens, tf)
        tf.flush()
        os.fsync(tf)
        yield tf.name


@patch('fitbit.Fitbit')
def test_fitbit_save_tokens(fb_mock, token_file):
    dut = Devices(config=token_file, name='pytest', instant_run=True)
    dut._load_tokens()
    assert dut._tokens == {
        'client_id': '123456',
        'client_secret': 'abcdefg',
        'access_token': 'zyx',
        'refresh_token': 'refresh_token',
        'expires_at': 123.567
    }
    dut._save_tokens({'access_token': 'access_token', 'refresh_token': 'refresh_token', 'expires_at': 9999.9})
    assert dut._tokens == {
        'client_id': '123456',
        'client_secret': 'abcdefg',
        'access_token': 'access_token',
        'refresh_token': 'refresh_token',
        'expires_at': 9999.9
    }
    with open(token_file, 'r') as tf:
        assert yaml.safe_load(tf) == {
            'client_id': '123456',
            'client_secret': 'abcdefg',
            'access_token': 'access_token',
            'refresh_token': 'refresh_token',
            'expires_at': 9999.9
        }


@patch('fitbit.Fitbit')
def test_fitbit_current_smoke(fb_mock, token_file):
    events = []
    def callback(plugin, payload):
        events.append(payload)

    fb_mock.return_value.time_series.return_value = {"steps": [{'value': '1000'}, {'value': '2000'}, {'value': '3000'}]}

    dut = Current(resources=['activities/steps', 'activities/distance'], config=token_file, name='pytest', instant_run=True)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)

    assert len(events) >= 1
    assert events[0] == {'activities/steps': 3000, 'activities/distance': 3000.0}


@patch('fitbit.Fitbit')
def test_fitbit_goal_smoke(fb_mock, token_file):
    events = []
    def callback(plugin, payload):
        events.append(payload)

    fb_mock.return_value.activities_daily_goal.return_value = {"goals": {'steps': 3000}}
    fb_mock.return_value.activities_weekly_goal.return_value = {"goals": {'steps': 6000}}
    fb_mock.return_value.body_fat_goal.return_value = {"goal": {"fat": 15.5}}

    dut = Goal(goals=['activities/daily/steps', 'activities/weekly/steps', 'body/fat'], config=token_file, name='pytest', instant_run=True)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)

    assert len(events) >= 1
    assert events[0] == {'activities/daily/steps': 3000, 'activities/weekly/steps': 6000, 'body/fat': 15.5}


@patch('fitbit.Fitbit')
def test_fitbit_devices_smoke(fb_mock, token_file):
    events = []
    def callback(plugin, payload):
        events.append(payload)

    fb_mock.return_value.get_devices.return_value = [{
        'battery': 'Empty',
        'batteryLevel': 10,
        'deviceVersion': 'Charge 2',
        'features': [],
        'id': 'abc',
        'lastSyncTime': '2018-12-23T10:47:40.000',
        'mac': 'AAAAAAAAAAAA',
        'type': 'TRACKER'
    }, {
        'battery': 'High',
        'batteryLevel': 95,
        'deviceVersion': 'Blaze',
        'features': [],
        'id': 'xyz',
        'lastSyncTime': '2019-01-02T10:48:39.000',
        'mac': 'FFFFFFFFFFFF',
        'type': 'TRACKER'
    }]

    dut = Devices(config=token_file, name='pytest', instant_run=True)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)

    assert len(events) >= 1
    assert events[0] == [{
        'battery': 'Empty',
        'battery_level': 10,
        'device_version': 'Charge 2',
        'features': [],
        'id': 'abc',
        'last_sync_time': '2018-12-23T10:47:40.000',
        'mac': 'AAAAAAAAAAAA',
        'type': 'TRACKER'
    }, {
        'battery': 'High',
        'battery_level': 95,
        'device_version': 'Blaze',
        'features': [],
        'id': 'xyz',
        'last_sync_time': '2019-01-02T10:48:39.000',
        'mac': 'FFFFFFFFFFFF',
        'type': 'TRACKER'
    }]
