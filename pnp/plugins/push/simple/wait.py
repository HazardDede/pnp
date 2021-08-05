"""Push: simple.Wait."""
from typing import Any

import asyncio

from pnp.plugins.push import AsyncPush
from pnp.typing import DurationLiteral, Payload
from pnp.utils import parse_duration_literal_float


class Wait(AsyncPush):
    """
    Performs a sleep operation to stop the execution flow for some time.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-wait
    """
    __REPR_FIELDS__ = ['interval']

    def __init__(self, wait_for: DurationLiteral, **kwargs: Any):
        super().__init__(**kwargs)
        self.interval = parse_duration_literal_float(wait_for)

    async def _push(self, payload: Payload) -> Payload:
        await asyncio.sleep(self.interval)
        return payload
