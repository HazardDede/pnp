import time

from pnp.plugins.pull.simple import Repeat, Count
from tests.plugins.helper import make_runner, start_runner


def test_count_pull():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = Count(name='pytest', from_cnt=0, to_cnt=5, wait=0.1)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(1)

    assert events == [0, 1, 2, 3, 4]


def test_count_pull_infinity():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = Count(name='pytest', from_cnt=0, to_cnt=None, wait=0.1)
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(1)

    expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert all([exp == actual for exp, actual in zip(expected, events)])


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
