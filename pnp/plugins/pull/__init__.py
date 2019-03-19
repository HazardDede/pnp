"""Basic stuff for implementing pull plugins."""

import multiprocessing as proc
import time
from abc import abstractmethod
from datetime import datetime

from schedule import Scheduler

from .. import Plugin
from ...utils import (auto_str_ignore, parse_duration_literal, StopCycleError,
                      interruptible_sleep, try_parse_bool)


@auto_str_ignore(['stopped', '_stopped', 'on_payload'])
class PullBase(Plugin):
    """
    Base class for pull plugins.
    The plugin has to implements `pull` to do the actual data retrieval / task.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stopped = proc.Event()

    @property
    def stopped(self):
        """Returns True if the pull is considered stopped; otherwise False."""
        return self._stopped.is_set()

    @abstractmethod
    def pull(self):
        """
        Performs the actual data retrieval / task.
        Returns:
            None.
        """
        raise NotImplementedError()  # pragma: no cover

    def on_payload(self, payload):
        """Callback for execution engine."""

    def notify(self, payload):
        """Call in subclass to emit some payload to the execution engine."""
        self.on_payload(self, payload)  # pylint: disable=too-many-function-args

    def stop(self):
        """Stops the plugin."""
        self._stopped.set()

    def _sleep(self, sleep_time=10):
        """Call in subclass to perform some sleeping."""
        def callback():
            if self.stopped:
                raise StopCycleError()
        interruptible_sleep(sleep_time, callback, interval=0.5)


class PollingError(Exception):
    """Base class for errors that occur during polling."""


class StopPollingError(Exception):
    """Raise this exception in child classes if you want to stop the polling scheduler."""


@auto_str_ignore(['_scheduler'])
class Polling(PullBase):
    """
    Base class for polling plugins.

    You may specify duration literals such as 60 (60 secs), 1m, 1h (...) to realize a periodic
    polling or cron expressions (*/1 * * * * > every min) to realize cron like behaviour.
    """
    __prefix__ = 'poll'

    def __init__(self, interval=60, instant_run=False, **kwargs):
        super().__init__(**kwargs)
        try:
            # Literals such as 60s, 1m, 1h, ...
            self._interval = parse_duration_literal(interval)
            self.is_cron = False
        except TypeError:
            # ... or a cron-like expression is valid
            from cronex import CronExpression
            self._interval = CronExpression(interval)
            self.is_cron = True

        self._scheduler = None
        self._instant_run = try_parse_bool(instant_run, False)

    def pull(self):
        self._scheduler = Scheduler()
        self._configure_scheduler(self._scheduler, self._run_schedule)

        if self._instant_run:
            self._scheduler.run_all()

        while not self.stopped:
            self._scheduler.run_pending()
            time.sleep(0.5)

    def _run_schedule(self):
        try:
            if self.is_cron:
                dtime = datetime.now()
                if not self._interval.check_trigger((dtime.year, dtime.month,
                                                     dtime.day, dtime.hour, dtime.minute)):
                    return  # It is not the time for the cron to trigger
            payload = self.poll()
            if payload is not None:
                self.notify(payload)
        except StopPollingError:
            self.stop()
        except Exception:  # pragma: no cover, pylint: disable=broad-except
            import traceback
            self.logger.error("[%s]\n%s", self.name, traceback.format_exc())

    def _configure_scheduler(self, scheduler, callback):
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
            scheduler.every(self._interval).seconds.do(callback)

    @abstractmethod
    def poll(self):
        """
        Implement in plugin components to do the actual polling.

        Returns: Returns the data for the downstream pipeline.

        """
        raise NotImplementedError()  # pragma: no cover
