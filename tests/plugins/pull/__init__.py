import asyncio
from collections import namedtuple
from contextlib import contextmanager, asynccontextmanager
from threading import Thread

from pnp.plugins.pull import Pull

Runner = namedtuple("Runner", ["pull", "start", "stop", "join", "raise_on_error"])
MqttMessage = namedtuple("MqttMessage", ["payload", "topic"])


def dummy_callback(plugin, payload):
    pass


@asynccontextmanager
async def start_runner(runner):
    runner.start()
    try:
        yield
    finally:
        await runner.stop()
        runner.join()
        runner.raise_on_error()


async def make_runner(plugin, callback):
    assert isinstance(plugin, Pull)
    plugin.callback(callback)

    error = None
    def _wrapper():
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(plugin.pull())
        except:
            import traceback
            nonlocal error
            error = traceback.format_exc()

    t = Thread(target=_wrapper)

    def start():
        t.start()

    async def stop():
        await plugin.stop()

    def join():
        t.join()

    def raise_if_applicable():
        assert error is None, error

    return Runner(pull=t, start=start, stop=stop, join=join, raise_on_error=raise_if_applicable)
