import time
from abc import abstractmethod

from schedule import Scheduler

from .. import Plugin
from ...utils import auto_str_ignore, parse_duration_literal, StopCycleError, interruptible_sleep


@auto_str_ignore(['stopped', 'on_payload'])
class PullBase(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stopped = False

    @abstractmethod
    def pull(self):
        raise NotImplementedError()  # pragma: no cover

    def on_payload(self, payload):
        pass  # pragma: no cover

    def notify(self, payload):
        self.on_payload(self, payload)

    def stop(self):
        self.stopped = True

    def _sleep(self, sleep_time):
        def callback():
            if self.stopped:
                raise StopCycleError()
        interruptible_sleep(sleep_time, callback, interval=0.5)


class PollingError(Exception):
    pass


@auto_str_ignore(['scheduler', 'on_payload'])
class Polling(PullBase):
    __prefix__ = 'poll'

    def __init__(self, interval=60, **kwargs):
        super().__init__(**kwargs)
        # polling interval in seconds
        self.interval = parse_duration_literal(interval)
        self.scheduler = None

    def pull(self):
        self.scheduler = Scheduler()
        self.scheduler.every(self.interval).seconds.do(self.run_schedule)
        while not self.stopped:
            try:
                self.scheduler.run_pending()
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
