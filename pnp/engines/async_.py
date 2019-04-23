"""Base implementation for asynchronous engines."""
from typing import Optional, Any

import asyncio

from . import Engine, RetryHandler, SimpleRetryHandler, PushExecutor
from ..models import TaskSet, TaskModel, PushModel
from ..plugins.pull import AsyncPullBase
from ..plugins.push import PushBase
from ..typing import Payload


class AsyncEngine(Engine):
    """Asynchronous engine."""
    def __init__(self, retry_handler: Optional[RetryHandler] = None):
        super().__init__()
        if not retry_handler:
            self.retry_handler = SimpleRetryHandler()  # type: RetryHandler
        else:
            self.retry_handler = retry_handler
        self.loop = asyncio.get_event_loop()
        self.tasks = None  # type: Optional[TaskSet]

    def _run(self, tasks: TaskSet) -> None:
        self.tasks = tasks
        coros = []
        for _, task in tasks.items():
            coros.append(self._start_task(task))

        try:
            self.loop.run_until_complete(asyncio.gather(*coros, loop=self.loop))
        except KeyboardInterrupt:
            self._shutdown()
        finally:
            # This check is only needed for Python 3.5 and below
            if hasattr(self.loop, "shutdown_asyncgens"):
                self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            if self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)

    def _stop(self) -> None:
        if not self.tasks:
            return
        self._shutdown()

    async def _start_task(self, task: TaskModel) -> None:
        """Start the given task."""
        def on_payload(plugin: Any, payload: Payload) -> None:  # pylint: disable=unused-argument
            for push in task.pushes:
                self.logger.debug(
                    "[Task-%s] Execution of item '%s' for push '%s'",
                    task.name,
                    payload,
                    push
                )
                self.loop.create_task(self._schedule_push(payload, push))

        task.pull.instance.on_payload = on_payload  # type: ignore

        while not task.pull.instance.stopped:
            try:
                if task.pull.instance.supports_async \
                        and isinstance(task.pull.instance, AsyncPullBase):
                    await task.pull.instance.async_pull()
                else:
                    await self.loop.run_in_executor(None, task.pull.instance.pull)
                if not task.pull.instance.stopped:
                    # Bad thing... Pulling exited unexpectedly
                    self.logger.error(
                        "[Task-%s] Pulling of '%s' exited unexpectedly",
                        task.name,
                        task.pull.instance,
                    )
            except KeyboardInterrupt:  # pragma: no cover
                self.logger.debug(
                    "[Task-%s] Pulling of '%s' hit a keyboard interrupt",
                    task.name,
                    task.pull.instance
                )
                self.loop.call_soon_threadsafe(task.pull.instance.stop)
            except:  # pylint: disable=bare-except
                # Bad thing... Pulling exited with exception
                import traceback
                self.logger.error(
                    "[Task-%s] Pulling of '%s' raised an error\n%s",
                    task.name,
                    task.pull.instance,
                    traceback.format_exc()
                )
            finally:
                await self._handle_pull_exit(task)

    async def _handle_pull_exit(self, task: TaskModel) -> None:
        if not task.pull.instance.stopped:
            directive = self.retry_handler.handle_error()
            if directive.abort:
                self.logger.error(
                    "[Task-%s] Pulling of '%s' exited due to retry limitation",
                    task.name,
                    task.pull.instance,
                )
            else:
                await asyncio.sleep(directive.wait_for, loop=self.loop)

    async def _stop_task(self, task: TaskModel) -> None:
        await self.loop.run_in_executor(None, task.pull.instance.stop)

    async def _schedule_push(self, payload: Payload, push: PushModel) -> None:
        assert isinstance(push, PushModel)
        assert isinstance(push.instance, PushBase)

        def _callback(result: Payload, dependency: PushModel) -> None:
            self.loop.create_task(self._schedule_push(result, dependency))

        await PushExecutor().async_execute(
            push.instance.name,
            payload,
            push,
            _callback
        )

    def _shutdown(self) -> None:
        assert self.tasks and isinstance(self.tasks, dict)

        loop = self.loop

        # Optionally show a message if the shutdown may take a while
        self.logger.info("Attempting graceful shutdown, press Ctrl+C again to exit...")

        # Do not show `asyncio.CancelledError` exceptions during shutdown
        # a lot of these may be generated, skip this if you prefer to see them
        def shutdown_exception_handler(loop, context):  # type: ignore
            if "exception" not in context \
                    or not isinstance(context["exception"], asyncio.CancelledError):
                loop.default_exception_handler(context)

        loop.set_exception_handler(shutdown_exception_handler)

        stop_tasks = asyncio.gather(
            *[self._stop_task(task) for _, task in self.tasks.items()],
            loop=loop
        )
        if loop.is_running():
            loop.create_task(stop_tasks)
        else:
            loop.run_until_complete(stop_tasks)

        # Handle shutdown gracefully by waiting for all tasks to be cancelled
        tasks = asyncio.gather(*asyncio.Task.all_tasks(loop=loop), loop=loop,
                               return_exceptions=True)
        tasks.add_done_callback(lambda t: loop.stop())
        # tasks.cancel()

        # Keep the event loop running until it is either destroyed or all
        # tasks have really terminated
        while not tasks.done() and not loop.is_closed():
            if not loop.is_running():
                loop.run_forever()
