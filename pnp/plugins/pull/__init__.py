import multiprocessing as proc
import time
from abc import abstractmethod

from schedule import Scheduler

from .. import Plugin
from ...utils import auto_str_ignore, parse_duration_literal, StopCycleError, interruptible_sleep, try_parse_bool


@auto_str_ignore(['stopped', '_stopped', 'on_payload'])
class PullBase(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stopped = proc.Event()

    @property
    def stopped(self):
        return self._stopped.is_set()

    @abstractmethod
    def pull(self):
        raise NotImplementedError()  # pragma: no cover

    def on_payload(self, payload):
        pass  # pragma: no cover

    def notify(self, payload):
        self.on_payload(self, payload)

    def stop(self):
        self._stopped.set()

    def _sleep(self, sleep_time):
        def callback():
            if self.stopped:
                raise StopCycleError()
        interruptible_sleep(sleep_time, callback, interval=0.5)


class PollingError(Exception):
    pass


class StopPollingError(Exception):
    """Raise this exception in child classes if you want to stop the polling scheduler."""
    pass


@auto_str_ignore(['_scheduler'])
class Polling(PullBase):
    __prefix__ = 'poll'

    def __init__(self, interval=60, instant_run=False, **kwargs):
        super().__init__(**kwargs)
        # polling interval in seconds
        self._interval = parse_duration_literal(interval)
        self._scheduler = None
        self._instant_run = try_parse_bool(instant_run, False)

    def pull(self):
        self._scheduler = Scheduler()
        self._scheduler.every(self._interval).seconds.do(self.run_schedule)

        if self._instant_run:
            self._scheduler.run_all()

        while not self.stopped:
            try:
                self._scheduler.run_pending()
            except StopPollingError:
                self.stop()
            except:  # pragma: no cover
                import traceback
                self.logger.error("[{name}]\n{error}".format(name=self.name, error=traceback.format_exc()))
            time.sleep(0.5)

    def run_schedule(self):
        payload = self.poll()
        self.notify(payload)

    @abstractmethod
    def poll(self):
        raise NotImplementedError()  # pragma: no cover
