"""Metric related helper methods and classes."""
import functools
from typing import Optional, Callable, Any

import prometheus_client as metric  # type: ignore

from .typing import Component, Payload
from .utils import CallbackTimer, Loggable

PULL_LABELS = ['pull']

PULL_EVENTS_EMITTED_TOTAL = metric.Counter(
    name='pull_events_emitted_total',
    documentation="Number of events emitted from the pull",
    labelnames=PULL_LABELS
)

PULL_EXITS_TOTAL = metric.Counter(
    name='pull_exits_total',
    documentation="Number of times the pull was restarted",
    labelnames=PULL_LABELS
)

PULL_FAILS_TOTAL = metric.Counter(
    name='pull_fails_total',
    documentation="Number of times the pull has failed",
    labelnames=PULL_LABELS
)

PULL_POLL_EXECUTION_SECONDS = metric.Histogram(
    name='pull_poll_execution_time_seconds',
    documentation="Measures execution time of a pull poll operation",
    labelnames=PULL_LABELS
)

PULL_STARTS_TOTAL = metric.Counter(
    name='pull_starts_total',
    documentation="Number of times the pull has started",
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

PUSH_EXECUTION_TIME_SECONDS = metric.Histogram(
    name='push_execution_time_seconds',
    documentation="Measures execution time of a push operation",
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

UDF_EXECUTION_TIME_SECONDS = metric.Histogram(
    name='udf_execution_time_seconds',
    documentation="Measures execution time of a udf operation",
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
    EXECUTION_TIME_METRIC = None  # type: Optional[metric.Histogram]
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

    def track_execution_time(self, elapsed: float) -> None:
        """Tracks the execution time of the component primary operation."""
        if not self.EXECUTION_TIME_METRIC:
            return
        self.EXECUTION_TIME_METRIC.labels(**self._labels).observe(elapsed)


class PullMetrics(ComponentMetrics):
    """Pull related metrics."""

    EVENTS_TOTAL_METRIC = PULL_EVENTS_EMITTED_TOTAL
    EXECUTION_TIME_METRIC = PULL_POLL_EXECUTION_SECONDS
    FAILS_TOTAL_METRIC = PULL_FAILS_TOTAL

    def __init__(self, pull: Component):
        super().__init__(pull=pull.name)

    def _reset_metrics(self) -> None:
        super()._reset_metrics()
        PULL_EXITS_TOTAL.labels(**self._labels).inc(0)
        PULL_STARTS_TOTAL.labels(**self._labels).inc(0)

    def track_start(self) -> None:
        """Track the start of a pull."""
        PULL_STARTS_TOTAL.labels(**self._labels).inc()

    def track_exit(self) -> None:
        """Track the exit of a pull."""
        PULL_EXITS_TOTAL.labels(**self._labels).inc()


class PushMetrics(ComponentMetrics):
    """Push related metrics."""

    EVENTS_TOTAL_METRIC = PUSH_EVENTS_PROCESSED_TOTAL
    EXECUTION_TIME_METRIC = PUSH_EXECUTION_TIME_SECONDS
    FAILS_TOTAL_METRIC = PUSH_EVENTS_FAILED_TOTAL

    def __init__(self, push: Component):
        super().__init__(push=push.name)


class UDFMetrics(ComponentMetrics):
    """User-defined-functions related metrics."""

    EVENTS_TOTAL_METRIC = UDF_EVENTS_PROCESSED_TOTAL
    EXECUTION_TIME_METRIC = UDF_EXECUTION_TIME_SECONDS
    FAILS_TOTAL_METRIC = UDF_EVENTS_FAILED_TOTAL

    def __init__(self, udf: Component):
        super().__init__(udf=udf.name)


def _track_call(fun_enter: Callable[[], None], fun_exit: Callable[[], None],
                fun_runtime: Callable[[float], None]) -> Callable[..., Payload]:
    """Decorator to track related metrics when calling a method.
    Will track the increase the event counter, the error count (if any) and observe the
    operation execution time."""
    def _inner(fun: Callable[..., Payload]) -> Callable[..., Payload]:
        def _observe(elapsed: float) -> None:
            fun_runtime(elapsed)

        @functools.wraps(fun)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            fun_enter()
            try:
                with CallbackTimer(_observe):
                    return fun(*args, **kwargs)
            except:
                fun_exit()
                raise

        @functools.wraps(fun)
        async def _async_wrapper(*args: Any, **kwargs: Any) -> Any:
            fun_enter()
            try:
                with CallbackTimer(_observe):
                    return await fun(*args, **kwargs)
            except:
                fun_exit()
                raise

        import inspect
        if inspect.iscoroutinefunction(fun):
            return _async_wrapper
        return _wrapper

    return _inner


def track_pull(metrics: PullMetrics) -> Callable[..., Payload]:
    """Decorator to track pull related metrics when running a pull.
    Will track the number of starts (maybe multiple due to errors) and the number of exits.
    """
    return _track_call(metrics.track_start, metrics.track_exit, lambda elapsed: None)


def track_event(metrics: ComponentMetrics) -> Callable[..., Payload]:
    """Decorator to track related metrics when calling a method.
    Will track the increase the event counter, the error count (if any) and observe the
    operation execution time."""

    return _track_call(metrics.track_event, metrics.track_fail, metrics.track_execution_time)
