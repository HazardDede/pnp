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
