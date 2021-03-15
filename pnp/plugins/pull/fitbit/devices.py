"""Pull: fitbit.Devices."""

import asyncio

from pnp.plugins.pull.fitbit.shared import FitbitBase
from pnp.typing import Payload
from pnp.utils import camel_to_snake, transform_dict_items


__EXTRA__ = 'fitbit'


class Devices(FitbitBase):
    """
    Requests details (battery, model, ...) about your fitbit devices / trackers
    associated to your account.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#fitbit-devices
    """
    async def _poll(self) -> Payload:
        devices = await asyncio.get_event_loop().run_in_executor(None, self.client.get_devices)
        return [transform_dict_items(d, keys_fun=camel_to_snake) for d in devices]  # type: ignore
