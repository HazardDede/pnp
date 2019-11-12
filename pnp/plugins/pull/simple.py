"""Simple pull plugins"""

import sys
import time
from datetime import datetime

from . import PullBase, Polling, AsyncPullBase
from ...utils import make_list, auto_str_ignore, parse_duration_literal_float
from ...validator import Validator


class Count(AsyncPullBase):
    """
    Emits every `wait` seconds a counting value which runs from `from_cnt` to `to_cnt`.
    If `to_cnt` is None will to count to infinity (or more precise sys.maxsize).

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/simple.Count/index.md

    """
    DEFAULT_INTERVAL = 5

    def __init__(self, from_cnt=0, to_cnt=None, wait=None, interval=None, **kwargs):
        super().__init__(**kwargs)
        self.from_cnt = int(from_cnt)
        self.to_cnt = to_cnt and int(to_cnt)
        self.interval = float(parse_duration_literal_float(
            interval or wait or self.DEFAULT_INTERVAL
        ))

    def pull(self):
        self._call_async_pull_from_sync()

    async def async_pull(self):
        to_cnt = sys.maxsize
        if self.to_cnt:
            to_cnt = self.to_cnt + 1
        for i in range(self.from_cnt, to_cnt):
            await self._async_sleep(self.interval)
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


class Repeat(AsyncPullBase):
    """
    Emits every `wait` seconds the same `repeat`.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/simple.Repeat/index.md

    """

    DEFAULT_INTERVAL = 5

    def __init__(self, repeat, wait=None, interval=None, **kwargs):
        super().__init__(**kwargs)
        self.repeat = repeat
        self.interval = float(parse_duration_literal_float(
            interval or wait or self.DEFAULT_INTERVAL
        ))

    def pull(self):
        self._call_async_pull_from_sync()

    async def async_pull(self):
        while not self.stopped:
            await self._async_sleep(self.interval)
            self.notify(self.repeat)
