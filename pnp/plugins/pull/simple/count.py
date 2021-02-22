"""Pull: simple.Count."""

import sys
import warnings
from typing import Any, Optional

from pnp.plugins.pull import AsyncPull
from pnp.typing import DurationLiteral
from pnp.utils import parse_duration_literal_float


class Count(AsyncPull):
    """
    Emits every `interval` seconds a counting value which runs from `from_cnt` to `to_cnt`.
    If `to_cnt` is None will to count to infinity (or more precise sys.maxsize).

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-count
    """
    __REPR_FIELDS__ = ['from_cnt', 'interval', 'to_cnt']

    DEFAULT_INTERVAL = 5

    def __init__(
            self, from_cnt: int = 0, to_cnt: Optional[int] = None,
            wait: Optional[DurationLiteral] = None, interval: Optional[DurationLiteral] = None,
            **kwargs: Any
    ):
        super().__init__(**kwargs)
        if wait is not None:
            warnings.warn(
                "Argument wait is deprecated, use interval instead",
                DeprecationWarning
            )

        self.from_cnt = int(from_cnt)
        self.to_cnt = to_cnt and int(to_cnt)
        self.interval = float(parse_duration_literal_float(
            interval or wait or self.DEFAULT_INTERVAL
        ))

    @property
    def can_exit(self) -> bool:  # pragma: no cover
        return True

    async def _pull(self) -> None:
        to_cnt = sys.maxsize
        if self.to_cnt:
            to_cnt = self.to_cnt + 1
        for i in range(self.from_cnt, to_cnt):
            await self._sleep(self.interval)
            self.notify(i)
            if self.stopped:
                break
