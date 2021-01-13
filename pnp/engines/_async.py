"""Base implementation for asynchronous engines."""

import asyncio
from typing import Optional

from pnp.engines._base import Engine, RetryHandler, SimpleRetryHandler, PushExecutor
from pnp.models import TaskSet, TaskModel, PushModel
from pnp.plugins.pull import SyncPull
from pnp.plugins.push import Push
from pnp.shared.async_ import async_sleep_until_interrupt
from pnp.typing import Payload
from pnp.utils import PY37


class AsyncEngine(Engine):
    """Asynchronous engine using asyncio."""

    __REPR_FIELDS__ = 'retry_handler'

    HEARTBEAT_INTERVAL = 0.5

    def __init__(
            self, retry_handler: Optional[RetryHandler] = None
    ):
        super().__init__()
        if not retry_handler:
            self.retry_handler = SimpleRetryHandler()  # type: RetryHandler
        else:
            self.retry_handler = retry_handler
        self.loop = asyncio.get_event_loop()

    async def _start(self, tasks: TaskSet) -> None:
        # Use the loop to create callbacks that was used to start the engine
        self.loop = asyncio.get_event_loop()
        coros = [self._wait_for_tasks_to_complete()]
        for _, task in tasks.items():
            coros.append(self._start_task(task))

        for coro in coros:
            self.loop.create_task(coro)

    async def _stop(self) -> None:
        if not self.tasks:
            return  # Nothing to stop

        await asyncio.gather(
            *[self._stop_task(task) for task in self.tasks.values()]
        )
        await self._wait_for_tasks_to_complete(True)

    async def _wait_for_tasks_to_complete(self, called_from_stop: bool = False) -> None:
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

        if not called_from_stop:
            await self.stop()

    async def _start_task(self, task: TaskModel) -> None:
        """Start the given task."""
        def on_payload_sync(pull: SyncPull, payload: Payload) -> None:
            _ = pull  # Fake usage
            for push in task.pushes:
                self.logger.debug(
                    "[Task-%s] Execution of item '%s' for push '%s'",
                    task.name,
                    payload,
                    push
                )
                self.loop.create_task(self._schedule_push(payload, push))

        task.pull.instance.callback(on_payload_sync)

        while not task.pull.instance.stopped:
            try:
                await task.pull.instance.pull()

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
                await self._stop_task(task)
                # self.loop.call_soon_threadsafe(task.pull.instance.stop)
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
            await task.pull.instance.stop()
            return

        directive = await self.retry_handler.handle_error()
        if directive.abort:
            self.logger.error(
                "[Task-%s] Pulling of '%s' exited due to retry limitation",
                task.name,
                task.pull.instance,
            )
            await task.pull.instance.stop()
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
        await instance.stop()

    async def _schedule_push(self, payload: Payload, push: PushModel) -> None:
        assert isinstance(push, PushModel)
        assert isinstance(push.instance, Push)

        def _callback(result: Payload, dependency: PushModel) -> None:
            self.loop.create_task(self._schedule_push(result, dependency))

        try:
            await PushExecutor().execute(
                push.instance.name,
                payload,
                push,
                _callback
            )
        except KeyboardInterrupt:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover, pylint: disable=broad-except
            self.logger.exception("Push '%s' failed", push.instance.name)
