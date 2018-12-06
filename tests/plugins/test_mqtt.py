import time

import paho.mqtt.publish
import pytest
from mock import patch

from pnp.plugins.pull.mqtt import MQTTPull
from pnp.plugins.push.mqtt import Publish
from tests.plugins.helper import make_runner, MqttMessage, start_runner, dummy_callback


@patch('paho.mqtt.client.Client')
def test_mqtt_pull(mock_client):
    mc = mock_client.return_value

    def callback(plugin, payload):
        assert payload['payload'] == "Payload"
        assert payload['topic'] == "test/device1/temperature"
        assert payload['levels'] == ["test", "device1", "temperature"]

    dut = MQTTPull(name='pytest', host='youneverknow', topic='test/#', port=1883)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(0.5)
        mc.on_connect(mc, "userdata", "flags", 0)
        mc.on_message(mc, "obj", MqttMessage(payload="Payload".encode('utf-8'), topic="test/device1/temperature"))

    mock_client.assert_called()
    mc.connect.assert_called()
    mc.connect.assert_called_with('youneverknow', 1883, 60)
    mc.username_pw_set.assert_not_called()
    mc.subscribe.assert_called()
    mc.subscribe.assert_called_with('test/#')
    mc.loop_forever.assert_called()


@patch('paho.mqtt.client.Client')
def test_mqtt_pull_credentials(mock_client):
    dut = MQTTPull(name='pytest', host='youneverknow', topic='test/#', port=1883)
    assert dut.user is None
    assert dut.password is None

    dut = MQTTPull(name='pytest', host='youneverknow', topic='test/#', port=1883, user="foo", password="bar")
    assert dut.user == "foo"
    assert dut.password == "bar"

    mc = mock_client.return_value
    runner = make_runner(dut, dummy_callback)
    with start_runner(runner):
        pass
    mock_client.assert_called()
    mc.username_pw_set.assert_called()
    mc.username_pw_set.assert_called_with("foo", "bar")


def test_mqtt_push(monkeypatch):

    def call_validator(**kwargs):
        assert kwargs.get('topic') == 'test/foo/bar'
        assert kwargs.get('hostname') == 'localhost'
        assert kwargs.get('port') == 1883
        assert kwargs.get('payload') == "This is the payload"
        assert not kwargs.get('retain')
        assert kwargs.get('auth') is None
        assert kwargs.get('qos') == 0

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar')
    dut.push("This is the payload")


def test_mqtt_push_with_qos():
    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', qos=1)
    assert dut.qos == 1
    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', qos="abc")
    assert dut.qos == 0
    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', qos=-1)
    assert dut.qos == 0
    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', qos=2)
    assert dut.qos == 2
    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', qos=3)
    assert dut.qos == 2


def test_mqtt_push_with_envelope_override(monkeypatch):

    def call_validator(**kwargs):
        assert kwargs.get('topic') == 'override'
        assert kwargs.get('hostname') == 'localhost'
        assert kwargs.get('port') == 1883
        assert kwargs.get('payload') == "This is the payload"
        assert kwargs.get('retain')
        assert kwargs.get('auth') is None
        assert kwargs.get('qos') == 2

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar')
    dut.push(dict(data="This is the payload", topic='override', retain=True, qos=2))

    dut = Publish(name='pytest', host='localhost')
    with pytest.raises(ValueError):
        dut.push(dict(data="This is the payload", retain=True, qos=2))


def test_mqtt_with_credentials(monkeypatch):

    def call_validator(**kwargs):
        assert kwargs.get('topic') == 'test/foo/bar'
        assert kwargs.get('hostname') == 'localhost'
        assert kwargs.get('port') == 1883
        assert kwargs.get('payload') == "This is the payload"
        assert not kwargs.get('retain')
        assert kwargs.get('auth') == {"username": "foo", "password": "bar"}

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', user="foo", password="bar")
    dut.push("This is the payload")


def test_mqtt_push_in_multi_mode(monkeypatch):
    call_count = 0

    def call_validator(**kwargs):
        nonlocal call_count
        call_count += 1
        assert kwargs.get('hostname') == 'localhost'
        assert kwargs.get('port') == 1883
        assert not kwargs.get('retain')
        assert kwargs.get('auth') is None
        assert kwargs.get('qos') == 0
        assert kwargs.get('topic') == 'test/foo/bar/attr{}'.format(str(call_count))
        assert kwargs.get('payload') == "payload{}".format(str(call_count))

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', multi=True)
    dut.push({"attr1": "payload1", "attr2": "payload2", "attr3": "payload3"})
    dut.push({"topic": "test/foo/bar/", "payload": {"attr4": "payload4"}})

    assert call_count == 4


def test_mqtt_push_in_multi_mode_without_dict(monkeypatch):
    def call_validator(**kwargs):
        assert False

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', multi=True)
    with pytest.raises(TypeError):
        dut.push("This is not a dictionary, biatch!")


def test_mqtt_push_in_multi_mode_with_error_not_aborting_other(monkeypatch):
    call_count = 0

    def call_validator(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise ValueError()
        assert kwargs.get('topic') == 'test/foo/bar/attr{}'.format(str(call_count))
        assert kwargs.get('payload') == "payload{}".format(str(call_count))

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = Publish(name='pytest', host='localhost', topic='test/foo/bar', multi=True)
    dut.push({"attr1": "payload1", "attr2": "payload2", "attr3": "payload3"})

    assert call_count == 3

