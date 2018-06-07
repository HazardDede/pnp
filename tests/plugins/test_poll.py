import time
from datetime import datetime

from pnp.plugins.pull import Polling
from tests.plugins.helper import make_runner, start_runner


def test_poll():
    class Dummy(Polling):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def poll(self):
            return datetime.now()

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = make_runner(Dummy(name='pytest', interval="1s"), callback)
    with start_runner(runner):
        time.sleep(5)

    assert len(events) >= 4
