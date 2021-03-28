"""Push: simple.Echo."""
from pnp.plugins.push import AsyncPush
from pnp.plugins.push.envelope import Envelope
from pnp.typing import Payload, Envelope as EnvelopeType


class Echo(AsyncPush):
    """
    This push simply logs the `payload` via the `logging` module.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-echo
    """

    @Envelope.unwrap
    async def _push_unwrap(self, envelope: EnvelopeType, payload: Payload) -> Payload:
        self.logger.info("Got '%s' with envelope '%s'", payload, envelope)
        # Payload as is. With envelope (if any)
        return {'payload': payload, **envelope} if envelope else payload

    async def _push(self, payload: Payload) -> Payload:
        return await self._push_unwrap(payload)  # pylint: disable=no-value-for-parameter
