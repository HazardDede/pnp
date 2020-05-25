"""Contains base classes for engines."""

import asyncio
import copy
from abc import abstractmethod
from datetime import datetime
from typing import Any, Callable, Optional

import attr

from pnp import validator
from pnp.models import TaskSet, PushModel
from pnp.plugins.push import AsyncPushBase
from pnp.selector import PayloadSelector
from pnp.typing import Payload
from pnp.utils import (
    Loggable, Singleton, parse_duration_literal, DurationLiteral, auto_str,
    is_iterable_but_no_str, auto_str_ignore
)


class NotSupportedError(Exception):
    """Is raised when a task is not supported by an engine."""


PushResultCallback = Callable[[Payload, PushModel], None]


@auto_str(__repr__=True)
class Engine(Loggable):
    """
    An engine is responsible for launching a defined set of tasks and the communication between
    pulls and and their associated pushes.

    A call to to an engine's `run(...)` method will block the calling thread until the engine
    decides the job is done (normally an external SIGTERM occurs)
    """
    async def run(self, tasks: TaskSet) -> None:
        """Run the given task set inside the engine."""
        return await self._run(tasks)

    @abstractmethod
    async def _run(self, tasks: TaskSet) -> None:
        """Run the given task set inside the engine. Override in child classes to do the hard
        work."""
        raise NotImplementedError()

    def stop(self) -> None:
        """Stop the engine."""
        self._stop()

    @abstractmethod
    def _stop(self) -> None:
        """Stop the engine. Override in child classes."""
        raise NotImplementedError()


@attr.s
class RetryDirective:
    """Contains directive information for engines on how to proceed in erroneous cases."""

    # If set to True, instructs the engine to abort the pull; otherwise retry the pull
    abort = attr.ib(converter=bool, type=bool, default=True)  # type: bool
    # Instructs the engine to wait some time before retrying the pull again
    wait_for = attr.ib(converter=parse_duration_literal, type=int, default=0)  # type: int
    # Just contextual information how many retries occurred so far
    retry_cnt = attr.ib(converter=int, type=int, default=0)  # type: int


@auto_str(__repr__=True)
class RetryHandler:
    """
    A retry handler comes into play when a pull component exits unexpectedly whether by breaking
    the actual loop or by error. The `RetryHandler` decides how to proceed further (wait and retry
    the pull or more sophisticated logic).
    """
    def __init__(self, **kwargs: Any):
        pass

    @abstractmethod
    async def handle_error(self) -> RetryDirective:
        """
        Asks the retry handler to handle an error.

        Returns:
            An instance of `RetryDirective`.
        """
        raise NotImplementedError()


class NoRetryHandler(RetryHandler):
    """Will instruct the engine to abort and not to retry the pull."""

    async def handle_error(self) -> RetryDirective:
        return RetryDirective(abort=True, wait_for=0, retry_cnt=1)


class SimpleRetryHandler(RetryHandler):
    """Simply instructs the engine to wait for the given amount of time after an error."""

    def __init__(self, retry_wait: DurationLiteral = 60, **kwargs: Any):
        super().__init__(**kwargs)
        self.retry_wait = parse_duration_literal(retry_wait)
        self.retry_count = 0

    async def handle_error(self) -> RetryDirective:
        self.retry_count += 1
        return RetryDirective(abort=False, wait_for=self.retry_wait, retry_cnt=self.retry_count)


class LimitedRetryHandler(SimpleRetryHandler):
    """Instructs the engine to wait for the given amout of time after an error. If the specified
     `max_retries` is hit the engine is instructed to abort the `pull`."""

    def __init__(self, max_retries: Optional[int] = 3, **kwargs: Any):
        super().__init__(**kwargs)
        self.max_retries = max_retries and int(max_retries)  # type: Optional[int]

    def _eval_abort(self, retry_count: int) -> bool:
        if self.max_retries is None or self.max_retries < 0:
            return False
        return retry_count > self.max_retries

    async def handle_error(self) -> RetryDirective:
        await super().handle_error()
        abort = self._eval_abort(self.retry_count)
        return RetryDirective(abort=abort, wait_for=self.retry_wait, retry_cnt=self.retry_count)


@auto_str_ignore(['last_error'])
class AdvancedRetryHandler(LimitedRetryHandler):
    """Works like the `LimitedRetryHandler` but will reset the retry count when a given amount of
    time between the current failure and the previous failure has passed."""

    def __init__(self, reset_retry_threshold: DurationLiteral = 60, **kwargs: Any):
        super().__init__(**kwargs)
        # Reset retry_count after x seconds of successful running
        self.reset_retry_threshold = parse_duration_literal(reset_retry_threshold)
        self.last_error = None  # type: Optional[datetime]

    async def handle_error(self) -> RetryDirective:
        # Handles two cases:
        # 1. Initial value -> no retries so far, the next is 1
        # 2. Reset retry count because threshold has reached, next try is 1
        if (self.last_error is None
                or (datetime.now() - self.last_error).total_seconds() > self.reset_retry_threshold):
            self.retry_count = 0

        self.last_error = datetime.now()
        directive = await super().handle_error()

        return RetryDirective(
            abort=directive.abort,
            wait_for=self.retry_wait,
            retry_cnt=self.retry_count
        )


class PushExecutor(Loggable, Singleton):
    """
    Given a payload and the push this helper actually "executes" the push by passing the payload
    after the (optional) selector did some magic to it.
    """

    async def _execute_internal(self, ident: str, payload: Payload, push: PushModel,
                                result_callback: Optional[PushResultCallback] = None) -> None:
        self.logger.debug("[%s] Selector: Applying '%s' to '%s'", ident, push.selector, payload)
        loop = asyncio.get_event_loop()
        # The selector expression has no async support
        # pylint: disable=no-member
        payload = await loop.run_in_executor(None, PayloadSelector.instance.eval_selector,
                                             push.selector, copy.deepcopy(payload))
        # pylint: enable=no-member

        # Only make the push if the selector wasn't evaluated to suppress the push
        if payload is not PayloadSelector.instance.suppress:  # pylint: disable=no-member
            self.logger.debug("[%s] Emitting '%s' to push '%s'", ident, payload, push.instance)
            if push.instance.supports_async and isinstance(push.instance, AsyncPushBase):
                push_result = await push.instance.async_push(payload=payload)
            else:
                push_result = await loop.run_in_executor(None, push.instance.push, payload)

            # Trigger any dependent pushes
            for dependency in push.deps:
                if result_callback:
                    # Delegate work back to the engine
                    self.logger.debug(
                        "[%s] Dependency callback is given. Delegating work back to engine", ident
                    )
                    result_callback(push_result, dependency)
                else:
                    # No delegation callback defined: The executor will recursively call itself
                    self.logger.debug(
                        "[%s] No callback is given. Recursively process dependencies", ident
                    )
                    await self.async_execute(ident, push_result, dependency)
        else:
            self.logger.debug(
                "[%s] Selector evaluated to suppress literal. Skipping the push", ident
            )

    async def async_execute(self, ident: str, payload: Payload, push: PushModel,
                            result_callback: Optional[PushResultCallback] = None) -> None:
        """
        Executes the given push (in an asynchronous context) by passing the specified payload.
        In concurrent environments there might be multiple executions in parallel.
        You may specify an `id` argument to identify related execution steps in the logs.
        Use the `result_callback` when the engine can take care of dependent pushes as well.
        The result and a dependent push will be passed via the callback. If the callback is not
        specified the PushExecute will execute them in a recursive manner.

        Args:
            ident (str): ID to identify related execution steps in the logs
                (makes sense in concurrent environments).
            payload (Any): The payload to pass to the push.
            push (PushModel): The push instance that has to process the payload.
            result_callback (callable): See explanation above.
        """

        validator.is_instance(PushModel, push=push)

        if result_callback and not callable(result_callback):
            self.logger.warning(
                "Result callback is given, but is not a callable. Callback will be ignored."
            )
            result_callback = None

        if push.unwrap and is_iterable_but_no_str(payload):
            length = len(payload)
            self.logger.debug("[%s] Unwrapping payload to %s individual items", ident, str(length))
            for item in payload:
                await self._execute_internal(ident, item, push, result_callback)
        else:
            await self._execute_internal(ident, payload, push, result_callback)
