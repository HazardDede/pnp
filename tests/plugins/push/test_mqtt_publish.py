import paho.mqtt.publish
import pytest

from pnp.plugins.push.mqtt import Publish


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


def test_mqtt_push_with_credentials(monkeypatch):

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
