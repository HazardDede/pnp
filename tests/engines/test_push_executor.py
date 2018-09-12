from pnp.engines import PushExecutor
from pnp.models import Push
from pnp.plugins.push.simple import Nop


def test_push_executor_with_selector():
    payload = dict(a="Actual payload", b="Another key that is ignored")
    push_instance = Nop(name='pytest')
    push = Push(instance=push_instance, selector="data.a", deps=[])
    dut = PushExecutor()
    dut.execute("id", payload, push, result_callback=None)

    assert push_instance.last_payload == "Actual payload"


def test_push_executor_with_deps():
    payload = "Actual payload"
    push_instance = Nop(name='pytest')
    dep_instance = Nop(name='pytest2')
    dep_push = Push(instance=dep_instance, selector=None, deps=[])
    push = Push(instance=push_instance, selector=None, deps=[dep_push])

    dut = PushExecutor()
    dut.execute("id", payload, push, result_callback=None)

    assert push_instance.last_payload == "Actual payload"
    assert dep_instance.last_payload == "Actual payload"

    def callback(payload, push):
        assert payload == "Actual payload"
        assert push == dep_push
    dut.execute("id", payload, push, result_callback=callback)
