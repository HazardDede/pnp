import time

import paho.mqtt.publish
from mock import patch

from pnp.plugins.pull.mqtt import MQTTPull
from pnp.plugins.push.mqtt import MQTTPush
from tests.plugins.helper import make_runner, MqttMessage, start_runner


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
    mc.subscribe.assert_called()
    mc.subscribe.assert_called_with('test/#')
    mc.loop.assert_called()


def test_mqtt_push(monkeypatch):

    def call_validator(**kwargs):
        assert kwargs.get('topic') == 'test/foo/bar'
        assert kwargs.get('hostname') == 'localhost'
        assert kwargs.get('port') == 1883
        assert kwargs.get('payload') == "This is the payload"
        assert not kwargs.get('retain')

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = MQTTPush(name='pytest', host='localhost', topic='test/foo/bar')
    dut.push("This is the payload")


def test_mqtt_push_with_envelope_override(monkeypatch):

    def call_validator(**kwargs):
        assert kwargs.get('topic') == 'override'
        assert kwargs.get('hostname') == 'localhost'
        assert kwargs.get('port') == 1883
        assert kwargs.get('payload') == "This is the payload"
        assert kwargs.get('retain')

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = MQTTPush(name='pytest', host='localhost', topic='test/foo/bar')
    dut.push(dict(data="This is the payload", topic='override', retain=True))
