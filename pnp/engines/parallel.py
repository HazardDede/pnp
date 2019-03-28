"""Base implementation for parallel engines."""

import copy
import multiprocessing
import threading
import time
from queue import Queue

from . import RetryHandler, PushExecutor, Engine, SimpleRetryHandler
from ..models import TaskModel, TaskSet
from ..utils import Loggable, auto_str, auto_str_ignore, sleep_until_interrupt
from ..validator import Validator


@auto_str(__repr__=True)
@auto_str_ignore(ignore_list=["queue", "stopped", "_runner"])
class StoppableRunner(Loggable):
    """
    Base implementation of a parallel runner that executes a `pull`. By default threading is used.

    For other implementations you have basically to override / adapt:
    * _make_shutdown_event() -> Create an event that can signal if this task should stop. The event
        should provide `is_set()` and `set()` methods (like the `Event` from `threading` does).
    * get_ident() -> Some unique identifier
    * start() -> Starts the runner. Start is async and will not block the current execution.
    * join(timeout=...) -> Wait for the runner to finish. Will block!
    * is_alive() -> Checks if the runner is currently running
    * terminate() -> Terminate the runner. Will only be called when the runner does not stop
        after `stop()` was called.
    """

    def __init__(self, task, queue, retry_handler):
        """
        Initializer.
        Args:
            task: Task to execute.
            queue: Queue to use for communication between runner and worker.
                Should provide `put(item)` method.
            retry_handler: Retry handler.
        """
        Validator.is_instance(TaskModel, task=task)
        self.task = task
        self.queue = queue
        self.stopped = self._make_shutdown_event()
        Validator.is_instance(RetryHandler, retry_handler=retry_handler)
        self.retry_handler = retry_handler
        self._runner = None

    @staticmethod
    def _make_shutdown_event():
        """Create an event that can signal if this task should stop. The event should provide
        `is_set()` and `set()` methods (like the `Event` from `threading` does)."""
        return threading.Event()

    @staticmethod
    def get_ident():
        """Return some unique identifier for this runner."""
        return threading.get_ident()

    def start(self):
        """Start the runner and the processing of the enveloped task."""
        if self._runner:
            raise RuntimeError("Runner is already started and cannot restart...")
        self._runner = threading.Thread(target=self._start_pull)
        self._runner.start()

    def join(self, timeout=None):
        """Wait for the runner to exit."""
        self._assert_runner()
        self._runner.join(timeout=timeout)

    def is_alive(self):
        """Check if the runner is still alive."""
        self._assert_runner()
        return self._runner.is_alive()

    def terminate(self):
        """Terminates the runner."""
        self.logger.warning(
            "Method terminate() on basic StoppableRunner is not supported.\n"
            "The thread will NOT terminate."
        )

    def _assert_runner(self):
        if not self._runner:
            raise RuntimeError("Runner is is not started")

    def _start_pull(self):
        def on_payload(plugin, payload):  # pylint: disable=unused-argument
            for push in self.task.pushes:
                self.logger.debug(
                    "[Task-%s] Queing item '%s' for push '%s'",
                    self.get_ident(),
                    payload,
                    push
                )
                self.queue.put((payload, push))

        self.task.pull.instance.on_payload = on_payload

        while not self.stopped.is_set():
            try:
                self.task.pull.instance.pull()
                if not self.stopped.is_set():
                    # Bad thing... Pulling exited unexpectedly
                    self.logger.error(
                        "[Task-%s] Pulling of '%s' exited unexpectedly",
                        self.get_ident(),
                        self.task.pull.instance,
                    )
            except KeyboardInterrupt:  # pragma: no cover
                self.logger.debug(
                    "[Task-%s] Pulling of '%s' hit a keyboard interrupt",
                    self.get_ident(),
                    self.task.pull.instance
                )
            except:  # pylint: disable=bare-except
                # Bad thing... Pulling exited with exception
                import traceback
                self.logger.error(
                    "[Task-%s] Pulling of '%s' raised an error\n%s",
                    self.get_ident(),
                    self.task.pull.instance,
                    traceback.format_exc()
                )
            finally:
                self._handle_pull_exit()

    def _handle_pull_exit(self):
        if not self.stopped.is_set():
            directive = self.retry_handler.handle_error()
            if directive.abort:
                self.logger.error(
                    "[Task-%s] Pulling of '%s' exited due to retry limitation",
                    self.get_ident(),
                    self.task.pull.instance,
                )
                self.stopped.set()
            else:
                sleep_until_interrupt(directive.wait_for, self.stopped.is_set)

    def stop(self):
        """Stop the runner gracefully."""
        self.logger.info(
            "[Task-%s] Got stopping signal: '%s'",
            self.get_ident(),
            self.task.name
        )
        self._assert_runner()
        self.stopped.set()
        self.task.pull.instance.stop()


@auto_str(__repr__=True)
class StoppableWorker(Loggable):
    """
    Base implementation of a worker that processes fetches items from the queue and delegates it to
    a push for further execution. By default threading is used.

    To stop the worker you should put the `stop_working_item` on the queue.

    For other implementations you have basically to override / adapt:
    * get_ident(): Some unique identifier
    * start(): Starts the worker. Start is async and will not block the current execution.
    * join(timeout=...): Wait for the worker to finish. Will block!
    * is_alive(): Checks if the worker is currently running
    * terminate(): Terminate the worker. Will only be called when the worker does not stop after
        receiving the `stop_working_item`.
    """
    def __init__(self, queue, stop_working_item):
        """
        Initializer.

        Args:
            queue: Queue to fetch processable items from. Should provide `get()` method.
            stop_working_item: Stop the worker when this item hits the queue.
        """
        self.queue = queue
        self.stop_working_item = stop_working_item
        self._worker = None

    @staticmethod
    def get_ident():
        """Return a unique identifier for this worker."""
        return threading.get_ident()

    def start(self):
        """Start this worker and begin to pull from the queue."""
        if self._worker:
            raise RuntimeError("Worker is already started and cannot restart...")
        self._worker = threading.Thread(target=self._process_queue)
        self._worker.start()

    def join(self, timeout=None):
        """Wait for the worker to exit."""
        self._assert_runner()
        self._worker.join(timeout=timeout)

    def is_alive(self):
        """Check if the worker is still running and alive."""
        self._assert_runner()
        return self._worker.is_alive()

    def terminate(self):
        """Termintes the worker forcefully."""
        self.logger.warning("Method terminate() on basic StoppableWorker is not supported.\n"
                            "The thread will NOT terminate.")

    def _assert_runner(self):
        if not self._worker:
            raise RuntimeError("Worker is is not started")

    def _process_queue(self):
        while True:
            try:
                payload = self.queue.get()
                if payload is self.stop_working_item:
                    self.logger.info("[Worker-%s] Got stopping signal", self.get_ident())
                    # Notify other worker as well
                    self.queue.put(self.stop_working_item)
                    break
                try:
                    # We assume payload is actual payload, push
                    payload, push = payload
                    PushExecutor().execute(
                        ident=str(self.get_ident()),
                        payload=payload,
                        push=push,
                        result_callback=lambda res, dep: self.queue.put((res, dep))
                    )
                finally:
                    # self.queue.task_done()
                    pass
            except KeyboardInterrupt:  # pragma: no cover
                pass
            except Exception:  # pragma: no cover, pylint: disable=broad-except
                import traceback
                self.logger.error("\n%s", traceback.format_exc())


@auto_str_ignore(ignore_list=["stop_working_item", "queue", "shutdown", "runner", "worker"])
class ParallelEngine(Engine):
    """Base implementation of a parallel engine.
    Spawns runner to process tasks and workers to handle any emitted results from `pull`
    components."""

    def __init__(self, queue_worker=3, retry_handler=None, stop_timeout=5):
        super().__init__()
        self.queue_worker = max(int(queue_worker), 1)
        self.retry_handler = retry_handler
        if self.retry_handler is None:
            self.retry_handler = SimpleRetryHandler()
        Validator.is_instance(RetryHandler, retry_handler=self.retry_handler)
        self.stop_working_item = object()
        self.queue = self._make_queue()
        self.runner = []
        self.worker = []
        self.shutdown = self._make_shutdown_event()
        self.stop_timeout = Validator.cast_or_none(int, stop_timeout) or 5

    def _make_worker(self):
        return StoppableWorker(self.queue, self.stop_working_item)

    def _make_runner(self, task, retry_handler):
        return StoppableRunner(task, self.queue, retry_handler=retry_handler)

    def _make_queue(self):  # pylint: disable=no-self-use
        return Queue()

    def _make_shutdown_event(self):  # pylint: disable=no-self-use
        # We might run the Engine in an isolated process.
        # So the multiprocessing.Event() is better suited.
        return multiprocessing.Event()

    def _run_queue_worker(self):
        n_worker = self.queue_worker
        for i in range(n_worker):
            thr = self._make_worker()
            thr.start()
            self.logger.info("[Worker-%s] Started (%s/%s)", thr.get_ident(), i + 1, n_worker)
            self.worker.append(thr)

    def _run_tasks(self, tasks):
        for _, task in tasks.items():
            thr = self._make_runner(task, copy.deepcopy(self.retry_handler))
            thr.start()
            self.logger.info("[Task-%s] Started for task '%s'", thr.get_ident(), task.name)
            self.runner.append(thr)

    def _stop_runner(self):
        for runner in self.runner:
            self.logger.debug("Stopping runner: %s", runner)
            runner.stop()

    def _stop_worker(self):
        self.logger.debug("Pushing stop_working_item on queue")
        self.queue.put(self.stop_working_item)

    def _stop_all(self):
        self._stop_runner()
        self._stop_worker()

    def _wait_for_all(self):
        for thr in self.runner + self.worker:
            thr.join(timeout=self.stop_timeout)
            if thr.is_alive():
                self.logger.warning("%s did not respond to stop command. Terminating...", thr)
                thr.terminate()

    def _run(self, tasks: TaskSet):
        for _, thr in tasks.items():
            if not isinstance(thr, TaskModel):
                raise TypeError("All items of argument 'tasks' are expected to be an instance "
                                "of 'Task'")

        self._run_queue_worker()
        self._run_tasks(tasks)
        try:
            while not self.shutdown.is_set():
                time.sleep(1)
        except KeyboardInterrupt:  # pragma: no cover
            pass
        self.logger.debug("Exited control loop. Stopping all threads gracefully")
        self._stop_all()
        self._wait_for_all()

    def _stop(self):
        self.shutdown.set()
