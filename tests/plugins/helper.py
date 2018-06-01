from collections import namedtuple
from threading import Thread
from pnp.plugins.pull import PullBase

Runner = namedtuple("Runner", ["pull", "start", "stop", "join", "error"])


def make_runner(plugin, callback):
    assert isinstance(plugin, PullBase)
    plugin.on_payload = callback

    error = None
    def _wrapper():
        try:
            plugin.pull()
        except:
            import traceback
            error = traceback.format_exc()

    t = Thread(target=_wrapper)

    def start():
        t.start()

    def stop():
        plugin.stop()

    def join():
        t.join()

    def get_error():
        return error

    return Runner(pull=t, start=start, stop=stop, join=join, error=get_error)
