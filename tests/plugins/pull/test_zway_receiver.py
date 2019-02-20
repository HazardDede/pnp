from pnp.plugins.pull.zway import ZwayReceiver


def _assert_this(result, device_name, raw_device, value, props=None):
    assert result is not None
    assert result['device_name'] == device_name
    assert result['raw_device'] == raw_device
    assert result['value'] == value
    assert type(result['value']) == type(value)
    if props is not None:
        assert result['props'] == props
    return None


def test_zway_http_valid():
    result = None
    def on_payload1(plugin, payload):
        nonlocal result
        result = payload

    dut = ZwayReceiver(name="pytest", url_format="%DEVICE%/%VALUE%", device_mapping=dict(dev1="alias"))
    dut.on_payload = on_payload1
    dut.notify(dict(full_path="http://localhost:8080/dev1/1?"))
    result = _assert_this(result, 'alias', 'dev1', 1)

    result = None
    dut.notify(dict(full_path="http://localhost:8080/unknown/1.1?"))
    result = _assert_this(result, 'unknown', 'unknown', 1.1)

    result = None
    dut.notify(dict(full_path="http://localhost:8080/unknown/1.1?sdfsdf/fsdjfds/sdfds"))
    result = _assert_this(result, 'unknown', 'unknown', 1.1)

    result = None
    dut.notify(dict(full_path="http://localhost:8080/dev1?value=1.1"))
    assert result is None

    dut = ZwayReceiver(name="pytest", url_format="%DEVICE%?value=%VALUE%", device_mapping=dict(dev1="alias"))
    dut.on_payload = on_payload1
    dut.notify(dict(full_path="http://localhost:8080/dev1?value=1"))
    result = _assert_this(result, 'alias', 'dev1', 1)

    dut = ZwayReceiver(name="pytest", url_format="/set?device=%DEVICE%&state=%VALUE%", device_mapping=dict(dev1="alias"))
    dut.on_payload = on_payload1
    dut.notify(dict(full_path="http://localhost:8080/set?device=dev1&state=1"))
    result = _assert_this(result, 'alias', 'dev1', 1)


def test_zway_http_ignore_unknown_devices():
    result = None
    def on_payload1(plugin, payload):
        nonlocal result
        result = payload

    # mode = mapping
    dut = ZwayReceiver(name="pytest", url_format="%DEVICE%/%VALUE%", device_mapping=dict(dev1="alias"),
                       ignore_unknown_devices=True)
    dut.on_payload = on_payload1
    dut.notify(dict(full_path="http://localhost:8080/dev1/1?"))
    result = _assert_this(result, 'alias', 'dev1', 1)

    result = None
    dut.notify(dict(full_path="http://localhost:8080/unknown/1.1?"))
    assert result is None

    # Now with mode = auto
    dut = ZwayReceiver(name="pytest", url_format="%DEVICE%/%VALUE%", mode='auto', ignore_unknown_devices=True)
    dut.on_payload = on_payload1
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-1/1?"))

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-1/1.1?"))
    assert result is None


def test_zway_http_advanced_mapping():
    result = None
    def on_payload1(plugin, payload):
        nonlocal result
        result = payload
    mapping = dict(dev1=dict(alias="alias", type="motion"))
    dut = ZwayReceiver(name="pytest", url_format="%DEVICE%/%VALUE%", device_mapping=mapping,
                       ignore_unknown_devices=True)
    dut.on_payload = on_payload1
    dut.notify(dict(full_path="http://localhost:8080/dev1/1?"))
    result = _assert_this(result, 'alias', 'dev1', 1, dict(type='motion'))


def test_zway_http_valid_with_mode_auto():
    result = None
    def on_payload1(plugin, payload):
        nonlocal result
        result = payload

    dut = ZwayReceiver(name="pytest", url_format="%DEVICE%/%VALUE%", device_mapping=dict(dev1="alias"), mode='auto')
    dut.on_payload = on_payload1

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-37/on?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-37', 'on', {'command_class': '37', 'mode': None, 'type': 'switch'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-38/55?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-38', 55, {'command_class': '38', 'mode': None, 'type': 'level'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-48-1/on?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-48-1', 'on', {'command_class': '48', 'mode': '1', 'type': 'motion'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-49-1/26.7?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-49-1', 26.7, {'command_class': '49', 'mode': '1', 'type': 'temperature'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-49-3/10?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-49-3', 10, {'command_class': '49', 'mode': '3', 'type': 'illumination'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-49-4/10?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-49-4', 10, {'command_class': '49', 'mode': '4', 'type': 'power'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-50-0/10?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-50-0', 10, {'command_class': '50', 'mode': '0', 'type': 'consumption'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-67-1/18?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-67-1', 18, {'command_class': '67', 'mode': '1', 'type': 'setpoint'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-128/67?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-128', 67, {'command_class': '128', 'mode': None, 'type': 'battery'})

    result = None
    dut.notify(dict(full_path="http://localhost:8080/BLUB/67?"))
    result = _assert_this(result, 'BLUB', 'BLUB', 67, {})


def test_zway_http_valid_with_mode_both():
    result = None
    def on_payload1(plugin, payload):
        nonlocal result
        result = payload

    dut = ZwayReceiver(name="pytest", url_format="%DEVICE%/%VALUE%", device_mapping=dict(dev1="alias"), mode='both')
    dut.on_payload = on_payload1
    dut.notify(dict(full_path="http://localhost:8080/dev1/1?"))
    result = _assert_this(result, 'alias', 'dev1', 1)

    result = None
    dut.notify(dict(full_path="http://localhost:8080/ZWayVDev_zway_21-0-37/on?"))
    result = _assert_this(result, '21', 'ZWayVDev_zway_21-0-37', 'on', {'command_class': '37', 'mode': None, 'type': 'switch'})
