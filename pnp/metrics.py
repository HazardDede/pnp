"""Metric related helper methods and classes."""
import functools
from typing import Optional, Callable, Any

import prometheus_client as metric  # type: ignore

from .typing import Component, Payload
from .utils import Loggable


PULL_LABELS = ['pull']

PULL_EVENTS_EMITTED_TOTAL = metric.Counter(
    name='pull_events_emitted_total',
    documentation="Number of events emitted from the pull",
    labelnames=PULL_LABELS
)

PULL_FAILS_TOTAL = metric.Counter(
    name='pull_fails_total',
    documentation="Number of times the pull has failed",
    labelnames=PULL_LABELS
)

PULL_RESTARTS_TOTAL = metric.Counter(
    name='pull_restarts_total',
    documentation="Number of times the pull was restarted",
    labelnames=PULL_LABELS
)


PUSH_LABELS = ['push']

PUSH_EVENTS_PROCESSED_TOTAL = metric.Counter(
    name='push_events_processed_total',
    documentation="Number of events the push has processed",
    labelnames=PUSH_LABELS
)

PUSH_EVENTS_FAILED_TOTAL = metric.Counter(
    name='push_events_failed_total',
    documentation="Number of events the push has failed to process",
    labelnames=PUSH_LABELS
)

UDF_LABELS = ['udf']

UDF_EVENTS_PROCESSED_TOTAL = metric.Counter(
    name='udf_events_processed_total',
    documentation="Number of events the udf has processed",
    labelnames=UDF_LABELS
)

UDF_EVENTS_FAILED_TOTAL = metric.Counter(
    name='udf_events_failed_total',
    documentation="Number of events the udf has failed to process",
    labelnames=UDF_LABELS
)


def start_httpd(port: int) -> None:
    """Start the metrics server."""
    # The start_http_server actually spawns a daemon thread
    metric.start_http_server(port)


class ComponentMetrics(Loggable):
    """Generic class for common metric operations. All metric components should subclass
    from this."""

    EVENTS_TOTAL_METRIC = None  # type: Optional[metric.Counter]
    FAILS_TOTAL_METRIC = None  # type: Optional[metric.Counter]

    def __init__(self, **labels: str):
        self._labels = labels
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        if self.EVENTS_TOTAL_METRIC:
            self.EVENTS_TOTAL_METRIC.labels(**self._labels).inc(0)
        if self.FAILS_TOTAL_METRIC:
            self.FAILS_TOTAL_METRIC.labels(**self._labels).inc(0)

    def track_event(self, amount: int = 1) -> None:
        """Tracks if one or more events passed this component."""
        if not self.EVENTS_TOTAL_METRIC:
            return

        amount = int(amount)
        if amount <= 0:
            self.logger.warning("Method `track_event` was called with an amount of 0"
                                "or less. This seems to be unintended.")
            return

        self.EVENTS_TOTAL_METRIC.labels(**self._labels).inc(amount)

    def track_fail(self) -> None:
        """Tracks if the component has failed for some reason."""
        if not self.FAILS_TOTAL_METRIC:
            return

        self.FAILS_TOTAL_METRIC.labels(**self._labels).inc()


class PullMetrics(ComponentMetrics):
    """Pull related metrics."""

    EVENTS_TOTAL_METRIC = PULL_EVENTS_EMITTED_TOTAL
    FAILS_TOTAL_METRIC = PULL_FAILS_TOTAL

    def __init__(self, pull: Component):
        super().__init__(pull=pull.name)


class PushMetrics(ComponentMetrics):
    """Push related metrics."""

    EVENTS_TOTAL_METRIC = PUSH_EVENTS_PROCESSED_TOTAL
    FAILS_TOTAL_METRIC = PUSH_EVENTS_FAILED_TOTAL

    def __init__(self, push: Component):
        super().__init__(push=push.name)


class UDFMetrics(ComponentMetrics):
    """User-defined-functions related metrics."""

    EVENTS_TOTAL_METRIC = UDF_EVENTS_PROCESSED_TOTAL
    FAILS_TOTAL_METRIC = UDF_EVENTS_FAILED_TOTAL

    def __init__(self, udf: Component):
        super().__init__(udf=udf.name)


def track_call(metrics: ComponentMetrics) -> Callable[..., Payload]:
    """Decorator to track related metrics when calling a method.
    Will track the event and if error count."""
    def _inner(fun: Callable[..., Payload]) -> Callable[..., Payload]:
        @functools.wraps(fun)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            metrics.track_event()
            try:
                return fun(*args, **kwargs)
            except:
                metrics.track_fail()
                raise
        return _wrapper
    return _inner


def async_track_call(metrics: ComponentMetrics) -> Callable[..., Payload]:
    """Async decorator to track related metrics when calling an async method.
    Will track the event and if error count."""
    def _inner(fun: Callable[..., Payload]) -> Callable[..., Payload]:
        @functools.wraps(fun)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            metrics.track_event()
            try:
                return await fun(*args, **kwargs)
            except:
                metrics.track_fail()
                raise

        return _wrapper
    return _inner
