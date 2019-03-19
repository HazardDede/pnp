"""Simple pull plugins"""

import sys
import time
from datetime import datetime

from . import PullBase, Polling
from ...utils import make_list, auto_str_ignore
from ...validator import Validator


class Count(PullBase):
    """
    Emits every `wait` seconds a counting value which runs from `from_cnt` to `to_cnt`.
    If `to_cnt` is None will to count to infinity.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/simple.Count/index.md

    """

    def __init__(self, from_cnt=0, to_cnt=None, wait=5, **kwargs):
        super().__init__(**kwargs)
        self.from_cnt = int(from_cnt)
        self.to_cnt = to_cnt and int(to_cnt)
        self.wait = float(wait)

    def pull(self):
        for i in range(self.from_cnt, self.to_cnt or sys.maxsize):
            self._sleep(self.wait)
            self.notify(i)
            if self.stopped:
                break


@auto_str_ignore(['jobs'])
class Cron(Polling):
    """
    Cron-like triggering of dependent pushes.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/simple.Cron/index.md
    """

    def __init__(self, expressions, **kwargs):
        super().__init__(interval=60, instant_run=False, **kwargs)
        self.expressions = make_list(expressions)

        from cronex import CronExpression
        self.jobs = [CronExpression(expression) for expression in self.expressions]

    def _configure_scheduler(self, scheduler, callback):
        scheduler.every().minute.at(":00").do(callback)

    def poll(self):
        for job in self.jobs:
            dtime = datetime.now()
            if job.check_trigger((dtime.year, dtime.month, dtime.day, dtime.hour, dtime.minute)):
                self.notify({'data': job.comment})


class CustomPolling(Polling):
    """
    Calls the specified callable every `interval`. The result of the callable is simply returned.
    This plugin is basically for _internal_ use only.
    """
    def __init__(self, scheduled_callable, **kwargs):
        super().__init__(**kwargs)
        self.scheduled_callable = scheduled_callable
        Validator.is_function(scheduled_callable=self.scheduled_callable)

    def poll(self):
        return self.scheduled_callable()


class Infinite(PullBase):
    """Just for demonstration purposes. DO NOT USE!"""

    def __init__(self, **kwargs):  # pragma: no cover, pylint: disable=useless-super-delegation
        super().__init__(**kwargs)

    def pull(self):  # pragma: no cover
        while True:
            time.sleep(0.5)


class Repeat(PullBase):
    """
    Emits every `wait` seconds the same `repeat`.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/simple.Repeat/index.md

    """

    def __init__(self, repeat, wait=5, **kwargs):
        super().__init__(**kwargs)
        self.repeat = repeat
        self.wait = float(wait)

    def pull(self):
        while not self.stopped:
            self._sleep(self.wait)
            self.notify(self.repeat)
