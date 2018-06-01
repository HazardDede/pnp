# For mocking
import paho.mqtt.publish

from pnp.plugins.pull.mqtt import MQTTPull
from pnp.plugins.push.mqtt import MQTTPush
from tests.plugins.helper import make_runner


# def test_mqtt_pull():
#     def callback(plugin, payload):
#         print(payload)
#
#     dut = MQTTPull(name='pytest', host='youneverknow', topic='test/#', port=1883)
#     runner = make_runner(dut, callback)
#     runner.start()
#
#     runner.stop()
#     runner.join()
#
#     print(runner.error())
#     if runner.error() is not None:
#         assert False, runner.error()


def test_mqtt_push(monkeypatch):

    def call_validator(**kwargs):
        assert kwargs.get('topic') == 'test/foo/bar'
        assert kwargs.get('hostname') == 'localhost'
        assert kwargs.get('port') == 1883
        assert kwargs.get('payload') == "This is the payload"

    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    dut = MQTTPush(name='pytest', host='localhost', topic='test/foo/bar')
    dut.push("This is the payload")
