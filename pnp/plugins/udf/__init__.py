"""Contains base stuff for user-defined functions in selector expressions."""

from abc import abstractmethod
from typing import Optional, Any

import cachetools  # type: ignore

from pnp.plugins import Plugin
from pnp.utils import (
    parse_duration_literal,
    DurationLiteral,
    make_hashable
)


class UserDefinedFunction(Plugin):
    """Base class for a user defined expression."""

    MAX_CACHE_SIZE = 12

    def __init__(self, throttle: Optional[DurationLiteral] = None, **kwargs: Any):
        """
        Initializer.

        Args:
            throttle: If set to a valid duration literal (e.g. 5m) the return value of the
              called functions will be cached for the given amount of time.
        """
        super().__init__(**kwargs)
        self.throttle = throttle and parse_duration_literal(throttle)
        self._cache = None
        if self.throttle:
            self._cache = cachetools.TTLCache(self.MAX_CACHE_SIZE, ttl=self.throttle)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._cache is None:
            return self.action(*args, **kwargs)

        hashable_args = (make_hashable(args), make_hashable(kwargs))
        try:
            return self._cache[hashable_args]
        except KeyError:
            res = self.action(*args, **kwargs)
            self._cache[hashable_args] = res
            return res

    @abstractmethod
    def action(self, *args: Any, **kwargs: Any) -> Any:
        """Actual definition of the hard-work of the user defined function."""
        raise NotImplementedError()
