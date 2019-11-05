"""Basic stuff for implementing pull plugins."""
import multiprocessing as proc
from abc import abstractmethod
from datetime import datetime
from typing import Any, Callable, Optional

import asyncio
from schedule import Scheduler  # type: ignore

from .. import Plugin
from ...shared.async_ import async_from_sync
from ...shared.async_ import async_sleep_until_interrupt
from ...typing import Payload
from ...utils import (auto_str_ignore, parse_duration_literal, try_parse_bool, DurationLiteral,
                      sleep_until_interrupt)


@auto_str_ignore(['stopped', '_stopped', 'on_payload'])
class PullBase(Plugin):
    """
    Base class for pull plugins.
    The plugin has to implements `pull` to do the actual data retrieval / task.
    """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._stopped = proc.Event()

    @property
    def stopped(self) -> bool:
        """Returns True if the pull is considered stopped; otherwise False."""
        return self._stopped.is_set()

    @property
    def supports_async(self) -> bool:
        """Returns True if the pull supports the asyncio engine; otherwise False."""
        return hasattr(self, 'async_pull')

    @abstractmethod
    def pull(self) -> None:
        """
        Performs the actual data retrieval / task.
        Returns:
            None.
        """
        raise NotImplementedError()  # pragma: no cover

    def on_payload(self, payload: Payload) -> None:
        """Callback for execution engine."""

    def notify(self, payload: Payload) -> None:
        """Call in subclass to emit some payload to the execution engine."""
        self.on_payload(self, payload)  # type: ignore  # pylint: disable=too-many-function-args

    def stop(self) -> None:
        """Stops the plugin."""
        self._stopped.set()

    def _sleep(self, sleep_time: float = 10) -> None:
        """Call in subclass to perform some sleeping."""
        sleep_until_interrupt(sleep_time, lambda: self.stopped, interval=0.5)


class AsyncPullBase(PullBase):
    """
    Base class for pulls that support the async engine.
    """
    def __init__(self, **kwargs: Any):  # pylint: disable=useless-super-delegation
        # Doesn't work without the useless-super-delegation
        super().__init__(**kwargs)

    async def async_pull(self) -> None:
        """Performs the actual data retrieval in a way that is compatible with the async engine."""
        raise NotImplementedError()

    def _call_async_pull_from_sync(self) -> None:
        """Calls the async pull from a sync context."""
        if not self.supports_async:
            raise RuntimeError(
                "Cannot run async pull version, cause async implementation is missing")

        async_from_sync(self.async_pull)

    async def _async_sleep(self, sleep_time: float = 10) -> None:
        """Call in subclass to perform some sleeping."""
        async def _interrupt() -> bool:
            return self.stopped
        await async_sleep_until_interrupt(sleep_time, _interrupt, interval=0.5)


class PollingError(Exception):
    """Base class for errors that occur during polling."""


class StopPollingError(Exception):
    """Raise this exception in child classes if you want to stop the polling scheduler."""


@auto_str_ignore(['_scheduler'])
class Polling(AsyncPullBase):
    """
    Base class for polling plugins.

    You may specify duration literals such as 60 (60 secs), 1m, 1h (...) to realize a periodic
    polling or cron expressions (*/1 * * * * > every min) to realize cron like behaviour.
    """
    __prefix__ = 'poll'

    def __init__(self, interval: DurationLiteral = 60, instant_run: bool = False, **kwargs: Any):
        super().__init__(**kwargs)

        try:
            # Literals such as 60s, 1m, 1h, ...
            self._poll_interval = parse_duration_literal(interval)
            self.is_cron = False
        except TypeError:
            # ... or a cron-like expression is valid
            from cronex import CronExpression  # type: ignore
            self._cron_interval = CronExpression(interval)
            self.is_cron = True

        self._is_running = False
        self._scheduler = None  # type: Optional[Scheduler]
        self._instant_run = try_parse_bool(instant_run, False)

    @property
    def supports_async_poll(self) -> bool:
        """Returns True if the poll natively supports async polling."""
        return hasattr(self, 'async_poll')

    def pull(self) -> None:
        self._call_async_pull_from_sync()

    async def async_pull(self) -> None:
        self._scheduler = Scheduler()
        self._configure_scheduler(self._scheduler, self._run_schedule)

        if self._instant_run:
            self._scheduler.run_all()

        while not self.stopped:
            self._scheduler.run_pending()
            await self._async_sleep(0.5)

        while self._is_running:  # Keep the loop alive until the job is finished
            await asyncio.sleep(0.5)

    def _run_schedule(self) -> None:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(self._async_run_schedule(), loop=loop)

    async def _async_run_schedule(self) -> None:
        if self._is_running:
            self.logger.warning("Polling job is still running. Skipping current run")
            return

        try:
            if self.is_cron:
                dtime = datetime.now()
                if not self._cron_interval.check_trigger((dtime.year, dtime.month,
                                                          dtime.day, dtime.hour, dtime.minute)):
                    return  # It is not the time for the cron to trigger

            self._is_running = True
            try:
                if isinstance(self, AsyncPolling) and hasattr(self, 'async_poll'):
                    payload = await self.async_poll()  # pylint: disable=no-member
                else:
                    payload = await asyncio.get_event_loop().run_in_executor(None, self.poll)
            finally:
                self._is_running = False

            if payload is not None:
                self.notify(payload)
        except StopPollingError:
            self.stop()
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
            # Scheduler executes every interval seconds to execute the poll
            scheduler.every(self._poll_interval).seconds.do(callback)

    @abstractmethod
    def poll(self) -> Payload:
        """
        Implement in plugin components to do the actual polling.

        Returns: Returns the data for the downstream pipeline.
        """
        raise NotImplementedError()  # pragma: no cover


class AsyncPolling(Polling):
    """
    Base class for polling plugins who can poll asynchronous.

    You may specify duration literals such as 60 (60 secs), 1m, 1h (...) to realize a periodic
    polling or cron expressions (*/1 * * * * > every min) to realize cron like behaviour.
    """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _call_async_poll_from_sync(self) -> Payload:
        """Calls the async pull from a sync context."""
        if isinstance(self, AsyncPolling) and hasattr(self, 'async_poll'):
            raise RuntimeError(
                "Cannot run async poll version, cause async implementation is missing.")

        return async_from_sync(self.async_poll)

    @abstractmethod
    async def async_poll(self) -> Payload:
        """
        Implement in plugin components to do the actual polling.

        Returns: Returns the data for the downstream pipeline.
        """
        raise NotImplementedError()  # pragma: no cover
