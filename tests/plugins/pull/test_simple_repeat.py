import time

from pnp.plugins.pull.simple import Repeat
from . import make_runner, start_runner


def test_repeat_pull():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = Repeat(name='pytest', repeat="Hello World", wait=0.1)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(1)

    assert len(events) >= 5
    assert all([p == "Hello World" for p in events])
