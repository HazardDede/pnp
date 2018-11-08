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

    dut = ZwayReceiver(name="pytest", url_format="%DEVICE%/%VALUE%", device_mapping=dict(dev1="alias"),
                       ignore_unknown_devices=True)
    dut.on_payload = on_payload1
    dut.notify(dict(full_path="http://localhost:8080/dev1/1?"))
    result = _assert_this(result, 'alias', 'dev1', 1)

    result = None
    dut.notify(dict(full_path="http://localhost:8080/unknown/1.1?"))
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
