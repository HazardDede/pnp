import copy
import signal
from typing import Any, Callable

from ..models import TaskSet, Push
from ..selector import PayloadSelector
from ..utils import Loggable, Singleton
from ..validator import Validator


class Engine (Loggable):
    """
    An engine is responsible for launching a defined set of tasks and the communication between pulls and and their
    associated pushes.

    A call to to an engine's `run(...)` method will block the calling thread until the engine decides the job is done
    (normally an external SIGTERM occurs)
    """
    def __init__(self):
        signal.signal(signal.SIGINT, self._exit_gracefully)
        signal.signal(signal.SIGTERM, self._exit_gracefully)

    def _exit_gracefully(self, signum, frame):
        self.logger.info("Got exit signal. Sending stop signal to engine")
        self._stop()

    def run(self, tasks: TaskSet):
        return self._run(tasks)

    def _run(self, tasks: TaskSet):
        raise NotImplementedError()

    def _stop(self):
        raise NotImplementedError()


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
            self.logger.debug("[{id}] Selector evaluated to suppress literal. Skipping the push")
