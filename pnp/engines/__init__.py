import copy
from abc import abstractmethod
from collections import namedtuple
from datetime import datetime
from typing import Any, Callable, Optional

from ..models import TaskSet, Push
from ..selector import PayloadSelector
from ..utils import Loggable, Singleton, parse_duration_literal, DurationLiteral, auto_str, interruptible_sleep, \
    StopCycleError
from ..validator import Validator

"""
Contains directive information for engines on how to proceed on failure cases.
abort -> Abort the pull
wait_for -> how long the pulling should be interrupted after the interrupt retry the pull
retry_cnt -> Just a context information.
"""
RetryDirective = namedtuple("RetryDirective", ["abort", "wait_for", "retry_cnt"])


class NotSupportedError(Exception):
    pass


@auto_str(__repr__=True)
class Engine (Loggable):
    """
    An engine is responsible for launching a defined set of tasks and the communication between pulls and and their
    associated pushes.

    A call to to an engine's `run(...)` method will block the calling thread until the engine decides the job is done
    (normally an external SIGTERM occurs)
    """
    def __init__(self):
        pass

    def _sleep(self, sleep_time):
        def callback():
            if self.stopped.is_set():
                raise StopCycleError()
        # We couldn't just easily call time.sleep(self, retry_wait), cause we cannot react on the stopping
        # signal. So have to manually sleep in 0.5 second steps and check for stopping signal
        interruptible_sleep(sleep_time, callback, interval=0.5)

    def run(self, tasks: TaskSet):
        return self._run(tasks)

    @abstractmethod
    def _run(self, tasks: TaskSet):
        raise NotImplementedError()

    def stop(self):
        self._stop()

    @abstractmethod
    def _stop(self):
        raise NotImplementedError()


@auto_str(__repr__=True)
class RetryHandler:
    """
    A retry handler comes into play when a pull component exits unexpectedly whether by breaking the actual loop
    or by error. The `RetryHandler` decides how to proceed further (wait and retry the pull or more sophisticated
    logic).
    """
    @abstractmethod
    def handle_error(self) -> RetryDirective:
        raise NotImplementedError()


class NoRetryHandler(RetryHandler):
    """Will instruct the engine to abort and not to retry the pull."""
    def handle_error(self) -> RetryDirective:
        return RetryDirective(abort=True, wait_for=0, retry_cnt=1)


class SimpleRetryHandler(RetryHandler):
    """Simply instructs the engine to wait for the given amount of time after an error."""
    def __init__(self, retry_wait: DurationLiteral = 60, **kwargs):
        self.retry_wait = parse_duration_literal(retry_wait)
        self.retry_count = 0

    def _incr_retry(self):
        self.retry_count += 1

    def handle_error(self) -> RetryDirective:
        self._incr_retry()
        return RetryDirective(abort=False, wait_for=self.retry_wait, retry_cnt=self.retry_count)


class LimitedRetryHandler(SimpleRetryHandler):
    """Instructs the engine to wait for the given amout of time after an error. If the specified `max_retries` is hit
    the engine is instructed to abort the `pull`."""
    def __init__(self, max_retries: Optional[int] = 3, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = Validator.cast_or_none(int, max_retries)

    def _eval_abort(self, retry_count: int) -> bool:
        if self.max_retries is None or self.max_retries < 0:
            return False
        return retry_count > self.max_retries

    def handle_error(self):
        super().handle_error()
        abort = self._eval_abort(self.retry_count)
        return RetryDirective(abort=abort, wait_for=self.retry_wait, retry_cnt=self.retry_count)


class AdvancedRetryHandler(LimitedRetryHandler):
    """Works like the `LimitedRetryHandler` but will reset the retry count when a given amount of time between the
    current failure and the previous failure has passed."""
    def __init__(self, reset_retry_threshold: DurationLiteral = 60, **kwargs):
        super().__init__(**kwargs)
        # Reset retry_count after x seconds of successful running
        self.reset_retry_threshold = parse_duration_literal(reset_retry_threshold)
        self.last_error = None

    def handle_error(self) -> RetryDirective:
        if self.last_error is None:
            # Initial value -> no retries so far, the next is 1
            self.retry_count = 0
        elif (datetime.now() - self.last_error).total_seconds() > self.reset_retry_threshold:
            # Reset retry count because threshold has reached, next try is 1
            self.retry_count = 0

        self.last_error = datetime.now()
        directive = super().handle_error()

        return RetryDirective(abort=directive.abort, wait_for=self.retry_wait, retry_cnt=self.retry_count)


class PushExecutor(Loggable, Singleton):
    """
    Given a payload and the push this helper actually "executes" the push by passing the payload after the (optional)
    selector did some magic to it.

    Examples:

        >>> payload = dict(a="This is the payload", b="another ignored key by selector")
        >>> from pnp.plugins.push.simple import Nop
        >>> push_instance = Nop(name='doctest')
        >>> push = Push(instance=push_instance, selector='data.a', deps=[])
        >>> PushExecutor().execute("doctest", payload, push)
        >>> push_instance.last_payload
        'This is the payload'

    """
    def execute(self, id: str, payload: Any, push: Push, result_callback: Callable = None) -> None:
        """
        Executes the given push by passing the specified payload.
        In concurrent environments there might be multiple executions in parallel. You may specify an `id` argument
        to identify related execution steps in the logs.
        Use the `result_callback` when the engine can take care of dependent pushes as well. The result and a dependent
        push will be passed via the callback. If the callback is not specified the PushExecute will execute them in
        a recursive manner.

        Args:
            id: ID to identify related execution steps in the logs (makes sense in concurrent environments).
            payload: The payload to pass to the push.
            push: The push instance that has to process the payload.
            result_callback: See explanation above.

        Returns:
            None.
        """
        Validator.is_instance(Push, push=push)

        if result_callback and not callable(result_callback):
            self.logger.warning("Result callback is given, but is not a callable. Callback will be ignored.")
            result_callback = None

        self.logger.debug("[{id}] Selector: Applying '{push.selector}' to '{payload}'".format(**locals()))
        # If selector is None -> returns a dot accessable dictionary if applicable
        # If selector is not None -> returns the evaluated expression (as a dot accessable dictionary
        # if applicable
        payload = PayloadSelector.instance.eval_selector(push.selector, copy.deepcopy(payload))

        # Only make the push if the selector wasn't evaluated to suppress the push
        if payload is not PayloadSelector.instance.SuppressLiteral:
            self.logger.debug("[{id}] Emitting '{payload}' to push '{push.instance}'".format(**locals()))
            push_result = push.instance.push(payload=payload)

            # Trigger any dependent pushes
            for dependency in push.deps:
                if result_callback:
                    # Delegate work back to the engine
                    self.logger.debug("[{id}] Dependency callback is given. Delegating work back to engine".format(
                        **locals()
                    ))
                    result_callback(push_result, dependency)
                else:
                    # No delegation callback defined: The executor will recursively call itself
                    self.logger.debug("[{id}] No callback is given. Recursively process dependencies".format(
                        **locals()
                    ))
                    self.execute(id, push_result, dependency)
        else:
            self.logger.debug("[{id}] Selector evaluated to suppress literal. Skipping the push".format(**locals()))
