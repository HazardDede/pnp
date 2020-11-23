import time

import pytest
from mock import patch

from pnp.plugins.pull.mqtt import Subscribe
from . import make_runner, MqttMessage, start_runner, dummy_callback


@pytest.mark.asyncio
async def test_mqtt_pull():
    with patch('paho.mqtt.client.Client') as mock_client:
        mc = mock_client.return_value

        def callback(plugin, payload):
            assert payload['payload'] == "Payload"
            assert payload['topic'] == "test/device1/temperature"
            assert payload['levels'] == ["test", "device1", "temperature"]

        dut = Subscribe(name='pytest', host='youneverknow', topic='test/#', port=1883)
        runner = await make_runner(dut, callback)
        async with start_runner(runner):
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


@pytest.mark.asyncio
async def test_mqtt_pull_credentials():
    dut = Subscribe(name='pytest', host='youneverknow', topic='test/#', port=1883)
    assert dut.user is None
    assert dut.password is None

    dut = Subscribe(name='pytest', host='youneverknow', topic='test/#', port=1883, user="foo", password="bar")
    assert dut.user == "foo"
    assert dut.password == "bar"

    with patch('paho.mqtt.client.Client') as mock_client:
        mc = mock_client.return_value
        runner = await make_runner(dut, dummy_callback)
        async with start_runner(runner):
            pass
        mock_client.assert_called()
        mc.username_pw_set.assert_called()
        mc.username_pw_set.assert_called_with("foo", "bar")
