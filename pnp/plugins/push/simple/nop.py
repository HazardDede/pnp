"""Push: simple.Nop."""
from typing import Any

from pnp.plugins.push import AsyncPush
from pnp.typing import Payload


class Nop(AsyncPush):
    """
    Executes no operation at all. A call to push(...) just returns the payload.
    This push is useful when you only need the power of the selector for dependent pushes.

    Nop = No operation OR No push ;-)

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-nop
    """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.last_payload = None

    async def _push(self, payload: Payload) -> Payload:
        self.last_payload = payload
        return payload
