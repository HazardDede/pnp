import asyncio
from collections import namedtuple
from threading import Thread

import async_generator

from pnp.plugins.pull import Pull, SyncPolling

Runner = namedtuple("Runner", ["pull", "start", "stop", "join", "raise_on_error", "events"])
MqttMessage = namedtuple("MqttMessage", ["payload", "topic"])


class CustomPolling(SyncPolling):
    """
    Calls the specified callable every `interval`. The result of the callable is simply returned.
    This plugin is basically for _internal_ use only.
    """
    def __init__(self, scheduled_callable, **kwargs):
        super().__init__(**kwargs)
        self.scheduled_callable = scheduled_callable

    def _poll(self):
        return self.scheduled_callable()


def dummy_callback(plugin, payload):
    pass


class CallbackMemory:
    def __init__(self):
        self.events = []

    def _callback(self, plugin, payload):
        self.events.append(payload)

    def bind(self, pull):
        pull.callback(self._callback)
        return self


@async_generator.asynccontextmanager
async def start_runner(runner):
    runner.start()
    try:
        yield
    finally:
        await runner.stop()
        runner.join()
        runner.raise_on_error()


async def make_runner(plugin, callback=None):
    assert isinstance(plugin, Pull)

    issued_events = []
    if callback:
        plugin.callback(callback)
    else:
        def callback(plugin, payload):
            issued_events.append(payload)
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

    def events():
        return events

    return Runner(
        pull=t,
        start=start,
        stop=stop,
        join=join,
        raise_on_error=raise_if_applicable,
        events=issued_events
    )
