"""Base implementation for asynchronous engines."""

import asyncio
import time
from typing import Optional, Any

from pnp.engines._base import Engine, RetryHandler, SimpleRetryHandler, PushExecutor
from pnp.models import TaskSet, TaskModel, PushModel
from pnp.plugins.push import PushBase
from pnp.shared.async_ import async_sleep_until_interrupt
from pnp.typing import Payload
from pnp.utils import auto_str_ignore, PY37


@auto_str_ignore(['loop', 'tasks'])
class AsyncEngine(Engine):
    """Asynchronous engine using asyncio."""

    HEARTBEAT_INTERVAL = 1.0

    def __init__(self, retry_handler: Optional[RetryHandler] = None):
        super().__init__()
        if not retry_handler:
            self.retry_handler = SimpleRetryHandler()  # type: RetryHandler
        else:
            self.retry_handler = retry_handler
        self.loop = asyncio.get_event_loop()
        self.tasks = None  # type: Optional[TaskSet]

    async def _run(self, tasks: TaskSet) -> None:
        self.tasks = tasks

        # We need to wait for tasks:
        # All pushes might be done, but pushes are pending / processing
        coros = [self._wait_for_tasks_to_complete()]
        for _, task in tasks.items():
            coros.append(self._start_task(task))

        try:
            await asyncio.gather(*coros)
            # self.loop.run_until_complete(asyncio.gather(*coros, loop=self.loop))
        except KeyboardInterrupt:
            self.stop()

    def _stop(self) -> None:
        if not self.tasks:
            return
        try:
            self._shutdown()
        except KeyboardInterrupt:
            # It' ok -> non-graceful shutdown
            self.logger.info("Forceful exit")

    async def _wait_for_tasks_to_complete(self) -> None:
        """Check if something is still running on the event loop (like running pushes) so that the
        event loop will not terminate but wait for pending tasks."""

        # pylint: disable=no-member
        fun_pending_tasks = asyncio.all_tasks if PY37 else asyncio.Task.all_tasks  # type: ignore
        fun_current_task = (
            asyncio.current_task if PY37  # type: ignore
            else asyncio.Task.current_task
        )
        # pylint: enable=no-member

        async def _pending_tasks_exist() -> bool:
            all_tasks = list(fun_pending_tasks())
            for task in all_tasks:
                if task is fun_current_task():  # Just in case
                    continue
                if task.done():  # Just in case
                    continue
                # Is a push running?
                if "coro=<AsyncEngine._schedule_push()" in str(task):
                    return True
                # Is a pull running?
                if "coro=<AsyncEngine._start_task()" in str(task):
                    return True
            return False

        await asyncio.sleep(self.HEARTBEAT_INTERVAL)
        while await _pending_tasks_exist():
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

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
                asyncio.run_coroutine_threadsafe(self._schedule_push(payload, push), self.loop)

        task.pull.instance.on_payload = on_payload  # type: ignore

        while not task.pull.instance.stopped:
            try:
                if task.pull.instance.supports_async:
                    await task.pull.instance.async_pull()  # type: ignore
                else:
                    await self.loop.run_in_executor(None, task.pull.instance.pull)

                if not task.pull.instance.stopped and not task.pull.instance.can_exit:
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
                self.logger.exception(
                    "[Task-%s] Pulling of '%s' raised an error",
                    task.name,
                    task.pull.instance.name
                )
            finally:
                await self._handle_pull_exit(task)

    async def _handle_pull_exit(self, task: TaskModel) -> None:
        if task.pull.instance.stopped:
            return
        if task.pull.instance.can_exit:
            task.pull.instance.stop()
            return

        directive = await self.retry_handler.handle_error()
        if directive.abort:
            self.logger.error(
                "[Task-%s] Pulling of '%s' exited due to retry limitation",
                task.name,
                task.pull.instance,
            )
            task.pull.instance.stop()
            return

        self.logger.info(
            "[Task-%s] Pulling of '%s' will restart in %s seconds",
            task.name,
            task.pull.instance,
            directive.wait_for
        )

        async def _interrupt() -> bool:
            return task.pull.instance.stopped
        await async_sleep_until_interrupt(directive.wait_for, _interrupt)

    async def _stop_task(self, task: TaskModel) -> None:
        self.logger.info("Stopping task %s", task.name)
        instance = task.pull.instance
        if instance.supports_async:
            await instance.async_stop()  # type: ignore
        else:
            await self.loop.run_in_executor(None, instance.stop)

    async def _schedule_push(self, payload: Payload, push: PushModel) -> None:
        assert isinstance(push, PushModel)
        assert isinstance(push.instance, PushBase)

        def _callback(result: Payload, dependency: PushModel) -> None:
            asyncio.run_coroutine_threadsafe(self._schedule_push(result, dependency), self.loop)

        try:
            await PushExecutor().async_execute(
                push.instance.name,
                payload,
                push,
                _callback
            )
        except KeyboardInterrupt:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover, pylint: disable=broad-except
            self.logger.exception("Push '%s' failed", push.instance.name)

    def _shutdown(self) -> None:
        assert self.tasks and isinstance(self.tasks, dict)

        loop = self.loop

        # Optionally show a message if the shutdown may take a while
        self.logger.info("Attempting graceful shutdown, press Ctrl+C again to exit forcefully...")

        # If it's running: Stop it!
        # Two scenarios:
        # 1. KeyboardInterrupt/OOM/Other Exception -> loop is already down
        # 2. stop() called -> We need to stop the loop (the code below assumes that the
        #   loop is down)
        self._wait_for_loop_to_stop(loop)

        # Do not show `asyncio.CancelledError` exceptions during shutdown
        # a lot of these may be generated, skip this if you prefer to see them
        def shutdown_exception_handler(loop, context):  # type: ignore
            if "exception" not in context \
                    or not isinstance(context["exception"], asyncio.CancelledError):
                loop.default_exception_handler(context)

        loop.set_exception_handler(shutdown_exception_handler)

        stop_tasks = asyncio.gather(
            *[self._stop_task(task) for task in self.tasks.values()],
            loop=loop
        )
        loop.run_until_complete(stop_tasks)

        loop.run_until_complete(self._wait_for_tasks_to_complete())

        # This check is only needed for Python 3.5 and below
        if hasattr(self.loop, "shutdown_asyncgens"):
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())  # type: ignore

    @staticmethod
    def _wait_for_loop_to_stop(loop: asyncio.AbstractEventLoop) -> None:
        if loop.is_running():
            loop.stop()
        for _ in range(10):
            if not loop.is_running():
                break
            time.sleep(1)
        if loop.is_running():
            raise RuntimeError("Event loop did not stop")
