import time
from datetime import datetime

from pnp.plugins.pull import StopPollingError
from pnp.plugins.pull.simple import CustomPolling
from tests.plugins.helper import make_runner, start_runner


def test_poll():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    def poll():
        return datetime.now()

    runner = make_runner(CustomPolling(name='pytest', interval="1s", scheduled_callable=poll), callback)
    with start_runner(runner):
        time.sleep(3)

    assert len(events) >= 2


def test_poll_for_aborting():
    events = []
    def callback(plugin, payload):
        events.append(payload)

    def poll():
        raise StopPollingError()

    runner = make_runner(CustomPolling(name='pytest', interval="1s", scheduled_callable=poll), callback)
    with start_runner(runner):
        time.sleep(1)

    assert len(events) == 0
