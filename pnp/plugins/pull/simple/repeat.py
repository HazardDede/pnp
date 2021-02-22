"""Pull: Repeat."""
import warnings
from typing import Any, Optional

from pnp.plugins.pull import AsyncPull, AsyncPullNowMixin
from pnp.typing import DurationLiteral
from pnp.utils import parse_duration_literal_float


class Repeat(AsyncPull, AsyncPullNowMixin):
    """
    Emits every `interval` seconds the same `repeat`.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-repeat

    """
    __REPR_FIELDS__ = ['interval', 'repeat']

    DEFAULT_INTERVAL = 5

    def __init__(
            self, repeat: Any, wait: Optional[DurationLiteral] = None,
            interval: Optional[DurationLiteral] = None, **kwargs: Any
    ):
        super().__init__(**kwargs)
        if wait is not None:
            warnings.warn(
                "Argument wait is deprecated, use interval instead",
                DeprecationWarning
            )

        self.repeat = repeat
        self.interval = float(parse_duration_literal_float(
            interval or wait or self.DEFAULT_INTERVAL
        ))

    async def _pull(self) -> None:
        while not self.stopped:
            await self._sleep(self.interval)
            await self._pull_now()

    async def _pull_now(self) -> None:
        self.notify(self.repeat)
