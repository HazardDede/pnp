"""Basic stuff for implementing pull plugins."""

import asyncio
import inspect
import multiprocessing as proc
from abc import abstractmethod
from datetime import datetime
from typing import Any, Callable, Optional

from schedule import Scheduler  # type: ignore
from typeguard import typechecked

from pnp.plugins import Plugin
from pnp.shared.async_ import (
    async_sleep_until_interrupt,
    run_sync
)
from pnp.typing import Payload
from pnp.utils import (
    parse_duration_literal,
    try_parse_bool,
    DurationLiteral,
    sleep_until_interrupt
)


class PollingError(Exception):
    """Base class for errors that occur during polling."""


class StopPollingError(Exception):
    """Raise this exception in child classes if you want to stop the polling scheduler."""


PullCallback = Callable[['Pull', Payload], None]


class Pull(Plugin):
    """
    Base class for pull plugins.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._assert_pull_compat()
        self._assert_pull_now_compat()

        self._stopped = proc.Event()
        self._callback: Optional[PullCallback] = None

    @property
    def stopped(self) -> bool:
        """Returns True if the pull is considered stopped; otherwise False."""
        return self._stopped.is_set()

    @property
    def can_exit(self) -> bool:
        """Override this property when an exit of the pull can be expected. This
        will prohibit the engine (or should) from raising notifications / errors
        or countermeasures like retries."""
        return False

    @property
    def supports_pull_now(self) -> bool:
        """Returns True if this instance supports an immediate pull; otherwise False."""
        return isinstance(self, (AsyncPullNowMixin, SyncPullNowMixin))

    @typechecked
    def callback(self, value: PullCallback) -> None:
        """Sets the payload callback on this instance."""
        self._callback = value

    def notify(self, payload: Payload) -> None:
        """Emit some payload to the execution engine."""
        if self._callback:
            self._callback(self, payload)

    def _assert_pull_compat(self) -> None:
        self._assert_abstract_compat((SyncPull, AsyncPull))
        self._assert_fun_compat('_pull')
        self._assert_fun_compat('_stop')

    def _assert_pull_now_compat(self) -> None:
        that = self
        if isinstance(that, (SyncPullNowMixin, AsyncPullNowMixin)):
            self._assert_fun_compat('_pull_now')

    async def pull(self) -> None:
        """Performs the actual data pulling."""
        pull_fun = getattr(self, '_pull')
        if inspect.iscoroutinefunction(pull_fun):
            await pull_fun()
            return
        await run_sync(pull_fun)

    async def pull_now(self) -> None:
        """Performs a pull now. Be careful: Not every pull does support this. Make sure to call
        supports_pull_now() previously to check the compatibility.
        """
        pull_now_fun = getattr(self, '_pull_now')
        if inspect.iscoroutinefunction(pull_now_fun):
            await pull_now_fun()
            return
        await run_sync(pull_now_fun)

    async def stop(self) -> None:
        """Stops the execution of this pull."""
        stop_fun = getattr(self, '_stop')
        if inspect.iscoroutinefunction(stop_fun):
            await stop_fun()
            return
        await run_sync(stop_fun)


class SyncPull(Pull):
    """Base class for synchronous pulls."""

    @abstractmethod
    def _pull(self) -> None:
        """
        Performs the actual data retrieval / task.
        Returns:
            None.
        """
        raise NotImplementedError()  # pragma: no cover

    def _stop(self) -> None:
        """Async variant of `stop()`."""
        self._stopped.set()

    def _sleep(self, sleep_time: float = 10) -> None:
        """Call in subclass to perform some sleeping."""
        sleep_until_interrupt(sleep_time, lambda: self.stopped, interval=0.5)


class AsyncPull(Pull):
    """
    Base class for asynchronous pulls.
    """
    @abstractmethod
    async def _pull(self) -> None:
        """Performs the actual data retrieval in a way that is compatible with the async engine."""
        raise NotImplementedError()

    async def _stop(self) -> None:
        """Async variant of `stop()`."""
        self._stopped.set()

    async def _sleep(self, sleep_time: float = 10) -> None:
        """Call in subclass to perform some sleeping."""
        async def _interrupt() -> bool:
            return self.stopped
        await async_sleep_until_interrupt(sleep_time, _interrupt, interval=0.5)


class SyncPullNowMixin:
    """Adds support to execute the pull right now without waiting for a specific trigger
    (like cron, special events, ...). This comes in handy for api triggers or the RunOnce pull."""

    def _pull_now(self) -> None:
        """Executes the pull right now."""
        raise NotImplementedError()


class AsyncPullNowMixin:
    """Adds support to asynchronously execute the pull right now without waiting for a
    specific trigger (like cron, special events, ...). This comes in handy for api
    triggers or the RunOnce pull."""

    async def _pull_now(self) -> None:
        """Asynchronously executes the pull right now."""
        raise NotImplementedError()


class Polling(AsyncPull, AsyncPullNowMixin):
    """
    Base class for polling plugins.

    You may specify duration literals such as 60 (60 secs), 1m, 1h (...) to realize a periodic
    polling or cron expressions (*/1 * * * * > every min) to realize cron like behaviour.
    """
    __REPR_FIELDS__ = ['interval', 'is_cron']

    def __init__(
        self, interval: Optional[DurationLiteral] = 60, instant_run: bool = False, **kwargs: Any
    ):
        super().__init__(**kwargs)

        self._assert_polling_compat()

        if interval is None:
            # No scheduled execution. Use endpoint `/trigger` of api to execute.
            self._poll_interval = None
            self.interval = None
            self.is_cron = False
        else:
            try:
                # Literals such as 60s, 1m, 1h, ...
                self._poll_interval = parse_duration_literal(interval)
                self.interval = interval
                self.is_cron = False
            except TypeError:
                # ... or a cron-like expression is valid
                from cronex import CronExpression  # type: ignore
                self._cron_interval = CronExpression(interval)
                self.interval = self._cron_interval
                self.is_cron = True

        self._is_running = False
        self._scheduler: Optional[Scheduler] = None
        self._instant_run = try_parse_bool(instant_run, False)

    def _assert_polling_compat(self) -> None:
        self._assert_abstract_compat((SyncPolling, AsyncPolling))
        self._assert_fun_compat('_poll')

    async def _pull(self) -> None:
        def _callback() -> None:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self._run_schedule())

        self._scheduler = Scheduler()
        self._configure_scheduler(self._scheduler, _callback)

        if self._instant_run:
            self._scheduler.run_all()

        while not self.stopped:
            self._scheduler.run_pending()
            await self._sleep(0.5)

        while self._is_running:  # Keep the loop alive until the job is finished
            await asyncio.sleep(0.1)

    async def _pull_now(self) -> None:
        await self._run_now()

    async def _run_now(self) -> Payload:
        """Runs the poll right now. It will not run, if the last poll is still running."""
        if self._is_running:
            self.logger.warning("Polling job is still running. Skipping current run")
            return

        self._is_running = True
        try:
            payload = await self.poll()

            if payload is not None:
                self.notify(payload)

            return payload
        finally:
            self._is_running = False

    async def _run_schedule(self) -> None:
        try:
            if self.is_cron:
                dtime = datetime.now()
                if not self._cron_interval.check_trigger((
                        dtime.year, dtime.month, dtime.day,
                        dtime.hour, dtime.minute
                )):
                    return  # It is not the time for the cron to trigger

            await self._run_now()
        except StopPollingError:
            await self._stop()
        except Exception:  # pragma: no cover, pylint: disable=broad-except
            self.logger.exception("Polling of '%s' failed", self.name)

    def _configure_scheduler(self, scheduler: Scheduler, callback: Callable[[], None]) -> None:
        """
        Configures the scheduler. You have to differ between "normal" intervals and
        cron like expressions by checking `self.is_cron`.

        Override in subclasses to fir the behaviour to your needs.

        Args:
            scheduler (schedule.Scheduler): The actual scheduler.
            callback (callable): The callback to call when the time is right.

        Returns:
            None
        """
        if self.is_cron:
            # Scheduler always executes at the exact minute to check for cron triggering
            scheduler.every().minute.at(":00").do(callback)
        else:
            # Only activate when an interval is specified
            # If not the only way is to trigger the poll by the api `trigger` endpoint
            if self._poll_interval:
                # Scheduler executes every interval seconds to execute the poll
                scheduler.every(self._poll_interval).seconds.do(callback)

    async def poll(self) -> Payload:
        """Performs polling."""
        poll_fun = getattr(self, '_poll')
        if inspect.iscoroutinefunction(poll_fun):
            return await poll_fun()
        return await run_sync(poll_fun)


class SyncPolling(Polling):
    """
    Base class for polling plugins who can poll synchronously.
    """

    @abstractmethod
    def _poll(self) -> Payload:
        """
        Implement in plugin components to do the actual polling.

        Returns: Returns the data for the downstream pipeline.
        """
        raise NotImplementedError()  # pragma: no cover


class AsyncPolling(Polling):
    """
    Base class for polling plugins who can poll asynchronously.
    """

    @abstractmethod
    async def _poll(self) -> Payload:
        """
        Implement in plugin components to do the actual polling.

        Returns: Returns the data for the downstream pipeline.
        """
        raise NotImplementedError()  # pragma: no cover
