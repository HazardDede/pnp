import multiprocessing
import threading

from . import Engine, RetryHandler, PushExecutor, NotSupportedError, SimpleRetryHandler, NoRetryHandler
from ..models import TaskSet
from ..validator import Validator


class SequentialEngine(Engine):
    """Sequential engine that only allows to run a single pull. It is more like a script execution and nothing
    is concurrent."""
    def __init__(self, retry_handler=None):
        super().__init__()
        Validator.is_instance(RetryHandler, allow_none=True, retry_handler=retry_handler)
        self.retry_handler = retry_handler
        if self.retry_handler is None:
            self.retry_handler = SimpleRetryHandler()
        self.stopped = multiprocessing.Event()
        self._task = None

    def _run(self, tasks: TaskSet):
        if len(tasks) < 1:
            return
        if len(tasks) > 1:
            raise NotSupportedError("The Sequential engine can only handle one task")

        task = tasks[list(tasks.keys())[0]]
        self._task = task

        def on_payload(plugin, payload):
            for push in task.pushes:
                try:
                    PushExecutor().execute('sequential', payload, push)
                except:  # pylint: disable=broad-except
                    import traceback
                    self.logger.error("\n{}".format(traceback.format_exc()))

        task.pull.instance.on_payload = on_payload
        task.pull.instance._stopped = self.stopped

        while not self.stopped.is_set():
            try:
                task.pull.instance.pull()
                if isinstance(self.retry_handler, NoRetryHandler):
                    self.stopped.set()

                if not self.stopped.is_set():
                    # Bad thing... Pulling exited unexpectedly
                    self.logger.error("Pulling of '{pull}' exited unexpectedly".format(
                        thread=threading.get_ident(),
                        pull=task.pull.instance,
                    ))
            except KeyboardInterrupt:
                self.stopped.set()
            except:   # pylint: disable=broad-except
                # Bad thing... Pulling exited with exception
                import traceback
                self.logger.error("Pulling of '{pull}' raised an error\n{error}".format(
                    thread=threading.get_ident(),
                    pull=task.pull.instance,
                    error=traceback.format_exc()
                ))
            finally:
                if not self.stopped.is_set():
                    directive = self.retry_handler.handle_error()
                    if directive.abort:
                        self.logger.error("Pulling of '{pull}' exited due to retry limitation".format(
                            thread=threading.get_ident(),
                            pull=task.pull.instance,
                        ))
                        self.stopped.set()
                    else:
                        self._sleep(directive.wait_for)

    def _stop(self):
        self.stopped.set()
