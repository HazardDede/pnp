"""Contains base stuff for user-defined functions in selector expressions."""

from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Any, Callable

from .. import Plugin
from ...metrics import UDFMetrics, track_event
from ...utils import auto_str_ignore, parse_duration_literal, DurationLiteral


@auto_str_ignore(['_metrics', '__call__'])
class UserDefinedFunction(Plugin):
    """Base class for a user defined expression."""

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
        self._last_call = None  # type: Optional[datetime]

        self._call = track_event(self.metrics)(self._call)  # type: Callable[..., Any]

    @property
    def metrics(self) -> UDFMetrics:
        """Return the metrics tracker. Override if necessary to provide custom
        implementation."""
        if not self._metrics:
            self._metrics = UDFMetrics(self)
        return self._metrics

    def _call(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore
        if not self.throttle:
            return self.action(*args, **kwargs)

        # Invariant: self.throttle is not None
        now = datetime.now()
        if self._last_call is None:
            res = self.action(*args, **kwargs)
            self._cache = res
            self._last_call = now
            return res

        # Invariant: self._last_call is not None
        span = now - self._last_call
        if span >= timedelta(seconds=self.throttle):
            res = self.action(*args, **kwargs)
            self._cache = res
            self._last_call = now
            return res

        # Invariant: span < delta(throttle)
        return self._cache

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call(*args, **kwargs)

    @abstractmethod
    def action(self, *args: Any, **kwargs: Any) -> Any:
        """Actual definition of the hard-work of the user defined function."""
        raise NotImplementedError()
