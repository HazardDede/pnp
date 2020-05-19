"""Contains so called trigger pulls that wrap polling pulls to decouple them from the
actual polling / scheduling mechanism. Instead of regular polling they can be run
by various external triggers (such as calling a web endpoint)."""

import asyncio

from pnp.config import load_pull_from_snippet
from pnp.typing import Payload
from . import PullBase, Polling, AsyncPolling
from ...utils import auto_str_ignore


@auto_str_ignore(['model'])
class TriggerBase(PullBase):
    """Base class for all trigger pulls. Manages instantiation of the wrapped polling
    component and provides helper methods for calling `poll` in sync and async
    variants."""

    def __init__(self, poll, **kwargs):
        super().__init__(**kwargs)
        self.model = self.model = load_pull_from_snippet(
            poll, base_path=self.base_path, name=self.name
        )
        instance = self.model.instance

        if not isinstance(instance, Polling):
            raise TypeError("The component to wrap has to be a polling component")

        self.wrapped = instance

    def _trigger_poll(self) -> Payload:
        return self.wrapped.poll()

    async def _async_trigger_poll(self) -> Payload:
        if self.wrapped.supports_async_poll and isinstance(self.wrapped, AsyncPolling):
            return await self.wrapped.async_poll()
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, self.wrapped.poll)

    def pull(self):
        pass  # pragma: no cover
