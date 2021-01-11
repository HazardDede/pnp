import asyncio
import time

import pnp.plugins.pull as pull
import pnp.plugins.push as push


class ErroneousPull(pull.Pull):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_count = 0

    def pull(self):
        self.call_count += 1
        raise ValueError(
            "Something went wrong for the {} time. Once again...".format(self.call_count))


class ErroneousPush(push.SyncPush):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_count = 0

    def _push(self, payload):
        self.call_count += 1
        raise ValueError(
            "Something went wrong for the {} time. Once again...".format(self.call_count))


class LongPoll(pull.Polling):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_count = 0

    def poll(self):
        time.sleep(10)
        self.call_count += 1
        return "Long polling done: {}".format(self.call_count)


class AsyncLongPoll(pull.AsyncPolling):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_count = 0

    def _poll(self):
        return self._call_async_poll_from_sync()

    async def poll(self):
        await asyncio.sleep(5)
        self.call_count += 1
        return "Long polling done: {}".format(self.call_count)