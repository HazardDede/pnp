"""Contains base classes for engines."""

import copy
from abc import abstractmethod, ABCMeta
from datetime import datetime
from typing import Any, Callable, Optional, Coroutine, Iterable

import pydantic
import typeguard
from typeguard import check_argument_types

from pnp import validator
from pnp.models import TaskSet, PushModel
from pnp.selector import PayloadSelector
from pnp.shared.async_ import run_sync
from pnp.typing import Payload
from pnp.utils import (
    Loggable,
    Singleton,
    parse_duration_literal,
    DurationLiteral,
    is_iterable_but_no_str,
    ReprMixin
)


class NotSupportedError(Exception):
    """Is raised when a task is not supported by an engine."""


# Signature of push result callback
PushResultCallback = Callable[[Payload, PushModel], None]

# Signature of a on engine started callback
OnStartedCallback = Callable[[], Coroutine[Any, Any, None]]

# Signature of a on engine stopped callback
OnStoppedCallback = Callable[[], Coroutine[Any, Any, None]]


class Engine(Loggable, ReprMixin, metaclass=ABCMeta):
    """
    An engine is responsible for launching a defined set of tasks and the communication between
    pulls and and their associated pushes.

    A call to to an engine's `run(...)` method will block the calling thread until the engine
    decides the job is done (normally an external SIGTERM occurs)
    """
    __REPR_FIELDS__ = 'is_running'

    def __init__(self) -> None:
        self._is_running = False
        self._tasks: Optional[TaskSet] = None
        self._on_started_callback: Optional[Any] = None
        self._on_stopped_callback: Optional[Any] = None

    @property
    def is_running(self) -> bool:
        """Returns True if this engine is currently running; otherwise False."""
        return self._is_running

    @property
    def tasks(self) -> Optional[TaskSet]:
        """Returns the tasks that are currently running; otherwise (non running)
        None is returned."""
        return self._tasks

    @property
    def on_started_callback(self) -> Optional[OnStartedCallback]:
        """Returns the callback that is called when the engine has started."""
        return self._on_started_callback

    @on_started_callback.setter
    def on_started_callback(self, value: Optional[OnStartedCallback]) -> None:
        """Sets the callback that is called when the engine has started."""
        check_argument_types()
        self._on_started_callback = value

    @property
    def on_stopped_callback(self) -> Optional[OnStoppedCallback]:
        """Returns the callback that is called when the engine has stopped."""
        return self._on_stopped_callback

    @on_stopped_callback.setter
    def on_stopped_callback(self, value: Optional[OnStoppedCallback]) -> None:
        """Sets the callback that is called when engine has stopped."""
        check_argument_types()
        self._on_stopped_callback = value

    async def start(self, tasks: TaskSet) -> None:
        """Run the given task set inside the engine."""
        if self.is_running:
            return

        self._tasks = tasks
        await self._start(tasks)
        self._is_running = True

        if self._on_started_callback is not None:
            assert callable(self._on_started_callback)
            await self._on_started_callback()

    @abstractmethod
    async def _start(self, tasks: TaskSet) -> None:
        """Run the given task set inside the engine. Override in child classes to do the hard
        work."""
        raise NotImplementedError()

    async def stop(self) -> None:
        """Stop the engine."""
        if not self.is_running:
            return

        if not self.tasks:
            return

        await self._stop()
        self._tasks = None
        self._is_running = False

        if self._on_stopped_callback is not None:
            assert callable(self._on_stopped_callback)
            await self._on_stopped_callback()

    @abstractmethod
    async def _stop(self) -> None:
        """Stop the engine. Override in child classes."""
        raise NotImplementedError()


class RetryDirective(pydantic.BaseModel):
    """Contains directive information for engines on how to proceed in erroneous cases."""

    # If set to True, instructs the engine to abort the pull; otherwise retry the pull
    abort: bool = True
    # Instructs the engine to wait some time before retrying the pull again
    wait_for: int = 0
    # Just contextual information how many retries occurred so far
    retry_cnt: int = 0

    @pydantic.validator('wait_for', pre=True)
    @classmethod
    def _wait_for_duration_literal_converter(cls, value: Any) -> int:
        typeguard.check_type('wait_for', value, DurationLiteral)  # type: ignore
        return parse_duration_literal(value)


class RetryHandler(ReprMixin, Loggable, metaclass=ABCMeta):
    """
    A retry handler comes into play when a pull component exits unexpectedly whether by breaking
    the actual loop or by error. The `RetryHandler` decides how to proceed further (wait and retry
    the pull or more sophisticated logic).
    """
    __REPR_FIELDS__: Iterable[str] = []

    def __init__(self, **kwargs: Any):
        super().__init__()

        for unused_param in kwargs:
            self.logger.warning("Argument '%s' is unused", unused_param)

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

    __REPR_FIELDS__ = ['retry_wait', 'retry_count']

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

    __REPR_FIELDS__ = ['max_retries']

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


class AdvancedRetryHandler(LimitedRetryHandler):
    """Works like the `LimitedRetryHandler` but will reset the retry count when a given amount of
    time between the current failure and the previous failure has passed."""

    __REPR_FIELDS__ = ['reset_retry_threshold']

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

    async def _internal(
            self, ident: str, payload: Payload, push: PushModel,
            result_callback: Optional[PushResultCallback] = None
    ) -> None:
        self.logger.debug("[%s] Selector: Applying '%s' to '%s'", ident, push.selector, payload)
        # The selector expression has no async support
        payload = await run_sync(
            PayloadSelector().eval_selector, push.selector, copy.deepcopy(payload)
        )

        if PayloadSelector().should_suppress(payload):
            self.logger.debug(
                "[%s] Selector evaluated to suppress literal. Skipping the push", ident
            )
            return

        self.logger.debug("[%s] Emitting '%s' to push '%s'", ident, payload, push.instance)
        push_result = await push.instance.push(payload)

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
                await self.execute(ident, push_result, dependency)

    async def execute(
            self, ident: str, payload: Payload, push: PushModel,
            result_callback: Optional[PushResultCallback] = None
    ) -> None:
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
            # Payload unwrapping
            length = len(payload)
            self.logger.debug("[%s] Unwrapping payload to %s individual items", ident, str(length))
            for item in payload:
                await self._internal(ident, item, push, result_callback)
        else:
            # Standard way
            await self._internal(ident, payload, push, result_callback)
