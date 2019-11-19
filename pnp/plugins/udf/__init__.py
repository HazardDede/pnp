"""Contains base stuff for user-defined functions in selector expressions."""

from abc import abstractmethod
from typing import Any, Callable, Optional

import cachetools  # type: ignore

from .. import Plugin
from ...metrics import UDFMetrics, track_event
from ...utils import (
    auto_str_ignore,
    DurationLiteral,
    make_hashable,
    parse_duration_literal
)


@auto_str_ignore(['_metrics', '_call', '_cache'])
class UserDefinedFunction(Plugin):
    """Base class for a user defined expression."""

    MAX_CACHE_SIZE = 12

    def __init__(self, throttle: Optional[DurationLiteral] = None, **kwargs: Any):
        """
        Initializer.

        Args:
            throttle: If set to a valid duration literal (e.g. 5m) the return value of the
                called functions will be cached for the amount of time.
        """
        super().__init__(**kwargs)
        self._metrics = None  # type: Optional[UDFMetrics]
        self.throttle = throttle and parse_duration_literal(throttle)
        self._cache = None
        if self.throttle:
            self._cache = cachetools.TTLCache(self.MAX_CACHE_SIZE, ttl=self.throttle)

        self._call = track_event(self.metrics)(self._call)  # type: Callable[..., Any]

    @property
    def metrics(self) -> UDFMetrics:
        """Return the metrics tracker. Override if necessary to provide custom
        implementation."""
        if not self._metrics:
            self._metrics = UDFMetrics(self)
        return self._metrics

    def _call(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore
        if self._cache is None:
            return self.action(*args, **kwargs)

        hashable_args = (make_hashable(args), make_hashable(kwargs))
        try:
            return self._cache[hashable_args]
        except KeyError:
            res = self.action(*args, **kwargs)
            self._cache[hashable_args] = res
            return res

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call(*args, **kwargs)

    @abstractmethod
    def action(self, *args: Any, **kwargs: Any) -> Any:
        """Actual definition of the hard-work of the user defined function."""
        raise NotImplementedError()
