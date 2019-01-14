from pnp.engines import PushExecutor
from pnp.models import PushModel
from pnp.plugins.push.simple import Nop


def test_push_executor_with_selector():
    payload = dict(a="Actual payload", b="Another key that is ignored")
    push_instance = Nop(name='pytest')
    push = PushModel(instance=push_instance, selector="data.a", unwrap=False, deps=[])
    dut = PushExecutor()
    dut.execute("id", payload, push, result_callback=None)

    assert push_instance.last_payload == "Actual payload"


def test_push_executor_with_deps():
    payload = "Actual payload"
    push_instance = Nop(name='pytest')
    dep_instance = Nop(name='pytest2')
    dep_push = PushModel(instance=dep_instance, selector=None, deps=[], unwrap=False)
    push = PushModel(instance=push_instance, selector=None, unwrap=False, deps=[dep_push])

    dut = PushExecutor()
    dut.execute("id", payload, push, result_callback=None)

    assert push_instance.last_payload == "Actual payload"
    assert dep_instance.last_payload == "Actual payload"

    call_cnt = 0
    def callback(payload, push):
        nonlocal call_cnt
        assert payload == "Actual payload"
        assert push == dep_push
        call_cnt += 1
    dut.execute("id", payload, push, result_callback=callback)
    assert call_cnt == 1


def test_push_executor_unwrap():
    input = ["one", "two", "three"]
    push_instance = Nop(name="pytest")
    dep_instance = Nop(name='pytest2')
    dep_push = PushModel(instance=dep_instance, selector=None, deps=[], unwrap=False)
    push = PushModel(instance=push_instance, selector=None, unwrap=True, deps=[dep_push])

    dut = PushExecutor()
    call_cnt = 0
    def callback(payload, push):
        nonlocal call_cnt
        assert payload in input
        assert push is dep_push
        call_cnt += 1
    dut.execute("id", input, push, result_callback=callback)
    assert call_cnt == 3


def test_push_executor_unwrap_selector():
    input = ["one", "two", "three"]
    push_instance = Nop(name="pytest")
    dep_instance = Nop(name='pytest2')
    dep_push = PushModel(instance=dep_instance, selector=None, deps=[], unwrap=False)
    push = PushModel(instance=push_instance, selector="str(data)[0]", unwrap=True, deps=[dep_push])

    dut = PushExecutor()
    call_cnt = 0
    def callback(payload, push):
        nonlocal call_cnt
        assert payload in ['o', 't']
        assert push is dep_push
        call_cnt += 1
    dut.execute("id", input, push, result_callback=callback)
    assert call_cnt == 3
