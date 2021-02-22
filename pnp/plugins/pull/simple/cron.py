"""Pull: Cron."""

from datetime import datetime
from typing import Any, List, Callable, Union

from cronex import CronExpression
from schedule import Scheduler

from pnp.plugins.pull import SyncPolling
from pnp.utils import make_list


class Cron(SyncPolling):
    """
    Cron-like triggering of dependent pushes.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-cron
    """

    __REPR_FIELDS__ = ['expressions']

    ONE_MINUTE = 60

    def __init__(self, expressions: Union[List[str], str], **kwargs: Any):
        super().__init__(interval=self.ONE_MINUTE, instant_run=False, **kwargs)
        self.expressions = make_list(expressions) or []
        self.jobs = [CronExpression(expression) for expression in self.expressions]

    def _configure_scheduler(self, scheduler: Scheduler, callback: Callable[[], None]) -> None:
        scheduler.every().minute.at(":00").do(callback)

    def _poll(self) -> None:
        for job in self.jobs:
            dtime = datetime.now()
            if job.check_trigger((dtime.year, dtime.month, dtime.day, dtime.hour, dtime.minute)):
                self.notify(job.comment)

    async def _pull_now(self) -> None:
        for job in self.jobs:
            self.notify(job.comment)
