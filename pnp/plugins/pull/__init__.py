from abc import abstractmethod

import time
from schedule import Scheduler

from .. import Plugin
from ...utils import auto_str_ignore, parse_interval


@auto_str_ignore(['stopped'])
class PullBase(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stopped = False

    @abstractmethod
    def pull(self):
        # TODO: Make a _pull
        raise NotImplementedError()

    def on_payload(self, payload):
        pass

    def notify(self, payload):
        # TODO: Make payload a dict (if it isn't)
        # TODO: Add a timestamp as meta
        # TODO: Add the inbounds name
        self.on_payload(self, payload)

    def stop(self):
        self.stopped = True


class PollingError(Exception):
    pass


@auto_str_ignore(['scheduler'])
class Polling(PullBase):
    __prefix__ = 'poll'

    def __init__(self, interval=60, **kwargs):
        super().__init__(**kwargs)
        # polling interval in seconds
        self.interval = parse_interval(interval)
        self.scheduler = None

    def pull(self):
        self.scheduler = Scheduler()
        self.scheduler.every(self.interval).seconds.do(self.run_schedule)
        while not self.stopped:
            try:
                self.scheduler.run_pending()
            except:
                import traceback
                self.logger.error("[{name}]\n{error}".format(name=self.name, error=traceback.format_exc()))
            time.sleep(1)

    def run_schedule(self):
        payload = self.poll()
        self.notify(payload)

    @abstractmethod
    def poll(self):
        raise NotImplementedError()
