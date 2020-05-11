"""Simple pull plugins"""

import asyncio
import sys
import time
from datetime import datetime

from pnp.config import load_pull_from_snippet
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

    @property
    def can_exit(self) -> bool:
        return True  # pragma: no cover

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
                self.notify(job.comment)


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


@auto_str_ignore(['model'])
class RunOnce(AsyncPullBase):
    """
    Takes another valid `plugins.pull.Polling` component and immediately executes it and ventures
    down the given `plugins.push` components. If no component is given it will simple execute the
    push chain.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/simple.RunOnce/index.md
    """

    def __init__(self, poll=None, **kwargs):
        super().__init__(**kwargs)
        self.model = None
        self.wrapped = None
        if poll:
            self.model = load_pull_from_snippet(poll, base_path=self.base_path, name=self.name)
            self.wrapped = self.model.instance

            if not isinstance(self.wrapped, Polling):
                raise TypeError("The component to wrap has to be a polling component")

    @property
    def can_exit(self) -> bool:
        return True  # pragma: no cover

    async def async_pull(self) -> None:
        if not self.wrapped:
            self.notify({})  # Just notify about an empty dict
        else:
            if self.wrapped.supports_async_poll:
                res = await self.wrapped.async_poll()
            else:
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(None, self.wrapped.poll)
            self.notify(res)


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

    async def async_pull(self):
        while not self.stopped:
            await self._async_sleep(self.interval)
            self.notify(self.repeat)
