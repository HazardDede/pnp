from pnp.plugins.pull import AsyncPolling, SyncPolling, SyncPull


class SyncPollingDummy(SyncPolling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _poll(self):
        return 42


class AsyncPollingDummy(AsyncPolling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _poll(self):
        return 42


class ErrorPollingDummy(SyncPolling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _poll(self):
        raise Exception("Crash on purpose!")


class NoPollingDummy(SyncPull):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _pull(self):
        pass

    def _poll(self):
        raise Exception("Do not call me!")
