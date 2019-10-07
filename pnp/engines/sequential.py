"""Engine implementation using a sequential workflow. Supports only one task."""

import multiprocessing
from typing import Optional

from .base import (Engine, RetryHandler, PushExecutor, NotSupportedError, SimpleRetryHandler,
                   NoRetryHandler)
from ..models import TaskSet, TaskModel
from ..typing import Payload
from ..utils import sleep_until_interrupt
from ..validator import Validator


class SequentialEngine(Engine):
    """Sequential engine that only allows to run a single pull. It is more like a script execution
    and nothing is concurrent."""
    def __init__(self, retry_handler: Optional[RetryHandler] = None):
        super().__init__()
        Validator.is_instance(RetryHandler, allow_none=True, retry_handler=retry_handler)
        self.retry_handler = retry_handler
        if not self.retry_handler:
            self.retry_handler = SimpleRetryHandler()
        self.stopped = multiprocessing.Event()
        self._task = None  # type: Optional[TaskModel]

    def _run(self, tasks: TaskSet) -> None:
        if not tasks:
            return
        if len(tasks) > 1:
            raise NotSupportedError("The Sequential engine can only handle one task")

        task = tasks[list(tasks.keys())[0]]
        self._task = task

        def on_payload(plugin: object, payload: Payload) -> None:  # pylint: disable=unused-argument
            for push in task.pushes:
                try:
                    PushExecutor().execute('sequential', payload, push)
                except:  # pylint: disable=bare-except
                    self.logger.exception("Push '%s' failed", push.instance.name)

        task.pull.instance.on_payload = on_payload  # type: ignore
        task.pull.instance._stopped = self.stopped  # pylint: disable=protected-access

        while not self.stopped.is_set():
            try:
                task.pull.instance.pull()
                if isinstance(self.retry_handler, NoRetryHandler):
                    self.stopped.set()

                if not self.stopped.is_set():
                    # Bad thing... Pulling exited unexpectedly
                    self.logger.error(
                        "Pulling of '%s' exited unexpectedly",
                        task.pull.instance,
                    )
            except KeyboardInterrupt:
                self.stopped.set()
            except:   # pylint: disable=bare-except
                # Bad thing... Pulling exited with exception
                self.logger.exception(
                    "Pulling of '%s' raised an error",
                    task.pull.instance.name
                )
            finally:
                if not self.stopped.is_set():
                    directive = self.retry_handler.handle_error()  # type: ignore
                    if directive.abort:
                        self.logger.error(
                            "Pulling of '%s' exited due to retry limitation",
                            task.pull.instance,
                        )
                        self.stopped.set()
                    else:
                        sleep_until_interrupt(directive.wait_for, self.stopped.is_set)

    def _stop(self) -> None:
        self.stopped.set()
