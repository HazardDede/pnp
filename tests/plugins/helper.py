from collections import namedtuple
from contextlib import contextmanager
from threading import Thread

from pnp.plugins.pull import PullBase

Runner = namedtuple("Runner", ["pull", "start", "stop", "join", "raise_on_error"])
MqttMessage = namedtuple("MqttMessage", ["payload", "topic"])


def dummy_callback(plugin, payload):
    pass


@contextmanager
def start_runner(runner):
    runner.start()
    yield
    runner.stop()
    runner.join()
    runner.raise_on_error()


def make_runner(plugin, callback):
    assert isinstance(plugin, PullBase)
    plugin.on_payload = callback

    error = None
    def _wrapper():
        try:
            plugin.pull()
        except:
            import traceback
            nonlocal error
            error = traceback.format_exc()

    t = Thread(target=_wrapper)

    def start():
        t.start()

    def stop():
        plugin.stop()

    def join():
        t.join()

    def raise_if_applicable():
        assert error is None, error

    return Runner(pull=t, start=start, stop=stop, join=join, raise_on_error=raise_if_applicable)
