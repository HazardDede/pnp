import json

from pnp.plugins.push.mqtt import Discovery


def test_push_mqtt_discovery(monkeypatch):
    call_cnt = 0
    calls = []
    def call_validator(*args, **kwargs):
        nonlocal call_cnt
        call_cnt += 1
        calls.append(kwargs)

    import paho.mqtt.publish
    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    config = {'friendly_name': 'pytest_sensor'}
    dut = Discovery(
        host='doesnotmatter',
        discovery_prefix='pytest',
        component='sensor',
        config=config,
        object_id='pytest_sensor',
        node_id='12345',
        name='pytest__push'
    )
    dut._push(10)

    assert call_cnt == 2
    # config
    payload = calls[0].pop('payload')
    assert calls[0] == {
        'topic': 'pytest/sensor/12345/pytest_sensor/config',
        'hostname': 'doesnotmatter', 'port': 1883, 'retain': True, 'auth': None, 'qos': 0
    }
    assert json.loads(payload) == {
        "friendly_name": "pytest_sensor",
        "state_topic": "pytest/sensor/12345/pytest_sensor/state",
        "json_attributes_topic": "pytest/sensor/12345/pytest_sensor/attributes"
    }
    # state
    assert calls[1] == {
        'topic': 'pytest/sensor/12345/pytest_sensor/state',
        'payload': 10,
        'hostname': 'doesnotmatter', 'port': 1883, 'retain': True, 'auth': None, 'qos': 0
    }


def test_push_mqtt_discovery_envelope_override(monkeypatch):
    call_cnt = 0
    calls = []
    def call_validator(*args, **kwargs):
        nonlocal call_cnt
        call_cnt += 1
        calls.append(kwargs)

    import paho.mqtt.publish
    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    config = {'friendly_name': 'pytest_sensor'}
    dut = Discovery(
        host='doesnotmatter',
        discovery_prefix='pytest',
        component='sensor',
        config=config,
        object_id='pytest_sensor',
        node_id='12345',
        name='pytest__push',
    )
    dut._push({'data': 10, 'object_id': 'object_override', 'node_id': 'node_override'})

    assert call_cnt == 2
    # config
    payload = calls[0].pop('payload')
    assert calls[0] == {
        'topic': 'pytest/sensor/node_override/object_override/config',
        'hostname': 'doesnotmatter', 'port': 1883, 'retain': True, 'auth': None, 'qos': 0,
    }
    assert json.loads(payload) == {
        "friendly_name": "pytest_sensor",
        "state_topic": "pytest/sensor/node_override/object_override/state",
        "json_attributes_topic": "pytest/sensor/node_override/object_override/attributes"
    }
    # state
    assert calls[1] == {
        'topic': 'pytest/sensor/node_override/object_override/state',
        'payload': 10,
        'hostname': 'doesnotmatter', 'port': 1883, 'retain': True, 'auth': None, 'qos': 0
    }


def test_push_mqtt_config_vars(monkeypatch):
    call_cnt = 0
    calls = []
    def call_validator(*args, **kwargs):
        nonlocal call_cnt
        call_cnt += 1
        calls.append(kwargs)

    import paho.mqtt.publish
    monkeypatch.setattr(paho.mqtt.publish, 'single', call_validator)

    config = {'friendly_name': 'pytest_sensor', 'object_id': '{{var::object_id}}', 'node_id': '{{var::node_id}}'}
    dut = Discovery(
        host='doesnotmatter',
        discovery_prefix='pytest',
        component='sensor',
        config=config,
        object_id='pytest_sensor',
        node_id='12345',
        name='pytest__push',
    )
    dut._push(10)

    assert call_cnt == 2
    # config
    assert json.loads(calls[0]['payload']) == {
        'friendly_name': 'pytest_sensor',
        'object_id': 'pytest_sensor',
        'node_id': '12345',
        'json_attributes_topic': 'pytest/sensor/12345/pytest_sensor/attributes',
        'state_topic': 'pytest/sensor/12345/pytest_sensor/state'
    }
