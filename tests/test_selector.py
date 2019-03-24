import pytest

from pnp.models import UDFModel
from pnp.plugins.udf.simple import Counter
from pnp.selector import PayloadSelector
from pnp.utils import EvaluationError


def test_simple_selector_expression():
    sel = "'even' if int(payload) % 2 == 0 else 'not even'"
    assert PayloadSelector.instance.eval_selector(sel, "5") == 'not even'
    assert PayloadSelector.instance.eval_selector(sel, "2") == 'even'


def test_complex_dict_selector_expression():
    sel = {
        "data": "lambda p: 'even' if int(p) % 2 == 0 else 'not even'",
        "lambda p: int(p)": 'data'
    }
    assert PayloadSelector.instance.eval_selector(sel, "5") == {
        'data': 'not even',
        5: 'data'
    }


def test_complex_list_selector_expression():
    sel = [1, 2, 'lambda p: int(p)', 'lambda p: int(p) + 1', 'lambda p: int(p) + 2', 6]
    assert PayloadSelector.instance.eval_selector(sel, "3") == [1, 2, 3, 4, 5, 6]


def test_simple_failing_selector_expression():
    sel = "'unknown variable name' + nobody_knowns_me"
    with pytest.raises(EvaluationError):
        PayloadSelector.instance.eval_selector(sel, "5")


def test_selector_register_udf():
    PayloadSelector.instance.register_udfs([
        UDFModel(name='countme', callable=Counter(name='pytest', init=1)),
        UDFModel(name="my_str", callable=str)
    ])
    assert PayloadSelector.instance.eval_selector("countme()", 'dummy') == 1
    assert PayloadSelector.instance.eval_selector("my_str(data)", 5) == '5'


def test_selector_a_lot():
    dut = PayloadSelector.instance

    assert dut.eval_selector('payload.k1', dict(k1='k1', k2='k2')) == 'k1'
    assert dut.eval_selector('suppress_me if int(payload) == 0 else int(payload)', 1) == 1
    assert dut.eval_selector('suppress_me if int(payload) == 0 else int(payload)', 0) is dut.suppress
    assert dut.eval_selector('on_off(data)', True) == 'on'

    dut.instance.register_custom_global('on_off_custom', lambda x: 'on' if x else 'off')
    assert dut.eval_selector('on_off_custom(data)', True) == 'on'
    assert dut.eval_selector('on_off_custom(data)', False) == 'off'

    payload = {'foo': {'bar': 1, 'baz': 2}}
    assert dut.eval_selector({
        "lambda payload: payload['foo']['bar']": 'baz',
        "foo": "lambda payload: payload['foo']['baz']",
        "lambda payload: payload['foo']['baz']": "lambda payload: payload['foo']['bar']"
    }, payload = payload) == {1: 'baz', 'foo': 2, 2: 1}

    assert dut.eval_selector([
        "foo",
        "lambda payload: payload['foo']['bar']",
        "lambda payload: payload['foo']['baz']",
        {"lambda payload: payload['foo']['bar']": "lambda payload: payload['foo']['baz']"},
        ["foo", "bar", "lambda payload: payload['foo']['bar']"]
    ], payload=payload) == ['foo', 1, 2, {1: 2}, ['foo', 'bar', 1]]

    assert dut.eval_selector("payload", payload=payload) == {'foo': {'bar': 1, 'baz': 2}}
    assert dut.eval_selector({"payload": "payload"}, payload=payload) == {'payload': 'payload'}
    assert dut.eval_selector({"payload": "lambda payload: payload"}, payload=payload) == {'payload': {'foo': {'bar': 1, 'baz': 2}}}

    with pytest.raises(EvaluationError) as e:
        dut.eval_selector("this one is not known", payload=payload)
    assert "Failed to evaluate 'this one is not known'" in str(e)

    with pytest.raises(EvaluationError) as e:
        dut.eval_selector(["lambda payload: known this is not"], payload=payload)
    assert "Your lambda is errorneous: 'lambda payload: known this is not'" in str(e)

    with pytest.raises(EvaluationError) as e:
        dut.eval_selector(["lambda payload: known"], payload=payload)
    assert "Error when running the selector lambda: 'lambda payload: known'" in str(e)

    assert dut.eval_selector({'str': 'str'}, payload=payload) == {'str': 'str'}
