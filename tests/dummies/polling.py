from pnp.plugins.pull import Polling, AsyncPolling, PullBase


class SyncPollingDummy(Polling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def poll(self):
        return 42


class AsyncPollingDummy(AsyncPolling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def poll(self):
        raise Exception("Don't call the sync version of pull")

    async def async_poll(self):
        return 42


class ErrorPollingDummy(Polling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def poll(self):
        raise Exception("Crash on purpose!")


class NoPollingDummy(PullBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def poll(self):
        raise Exception("Do not call me!")
