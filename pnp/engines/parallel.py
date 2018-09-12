import copy
import multiprocessing
import threading
import time
from queue import Queue

from . import RetryHandler, PushExecutor, Engine, SimpleRetryHandler
from ..models import Task, TaskSet
from ..utils import Loggable, StopCycleError, interruptible_sleep, auto_str, auto_str_ignore
from ..validator import Validator


@auto_str(__repr__=True)
@auto_str_ignore(ignore_list=["queue", "stopped", "_runner"])
class StoppableRunner(Loggable):
    """
    Base implementation of a parallel runner that executes a `pull`. By default threading is used.

    For other implementations you have basically to override / adapt:
    * _make_shutdown_event() -> Create an event that can signal if this task should stop. The event should provide
                                `is_set()` and `set()` methods (like the `Event` from `threading` does).
    * get_ident() -> Some unique identifier
    * start() -> Starts the runner. Start is async and will not block the current execution.
    * join(timeout=...) -> Wait for the runner to finish. Will block!
    * is_alive() -> Checks if the runner is currently running
    * terminate() -> Terminate the runner. Will only be called when the runner does not stop after `stop()` was called.
    """

    def __init__(self, task, queue, retry_handler):
        """
        Initializer.
        Args:
            task: Task to execute.
            queue: Queue to use for communication between runner and worker. Should provide `put(item)` method.
            retry_handler: Retry handler.
        """
        Validator.is_instance(Task, task=task)
        self.task = task
        self.queue = queue
        self.stopped = self._make_shutdown_event()
        Validator.is_instance(RetryHandler, retry_handler=retry_handler)
        self.retry_handler = retry_handler
        self._runner = None

    @staticmethod
    def _make_shutdown_event():
        return threading.Event()

    @staticmethod
    def get_ident():
        return threading.get_ident()

    def start(self):
        if self._runner:
            raise RuntimeError("Runner is already started and cannot restart...")
        self._runner = threading.Thread(target=self._start_pull)
        self._runner.start()

    def join(self, timeout=None):
        self._assert_runner()
        self._runner.join(timeout=timeout)

    def is_alive(self):
        self._assert_runner()
        return self._runner.is_alive()

    def terminate(self):
        self.logger.warn("Method terminate() on basic StoppableRunner is not supported. The thread will NOT terminate.")

    def _assert_runner(self):
        if not self._runner:
            raise RuntimeError("Runner is is not started")

    def _sleep(self, sleep_time):
        def callback():
            if self.stopped.is_set():
                raise StopCycleError()
        # We couldn't just easily call time.sleep(self, retry_wait), cause we cannot react on the stopping
        # signal. So have to manually sleep in 0.5 second steps and check for stopping signal
        interruptible_sleep(sleep_time, callback, interval=0.5)

    def _start_pull(self):
        def on_payload(plugin, payload):
            # A task / inbound might have multiple pushes / outbounds associated
            for push in self.task.pushes:
                self.logger.debug("[Task-{thread}] Queing item '{item}' for push '{push}'".format(
                    thread=self.get_ident(),
                    item=payload,
                    push=push
                ))
                # We do not evaluate the selector here. We let this handle the worker process. why?
                # Cause the selector might take some time... and we do not need a try... catch... here
                # Much can go wrong with the selector, if it does it will only cause issues with a single push
                self.queue.put((payload, push))

        self.task.pull.instance.on_payload = on_payload

        while not self.stopped.is_set():
            try:
                self.task.pull.instance.pull()
                if not self.stopped.is_set():
                    # Bad thing... Pulling exited unexpectedly
                    self.logger.error("[Task-{thread}] Pulling of '{pull}' exited unexpectedly".format(
                        thread=self.get_ident(),
                        pull=self.task.pull.instance,
                    ))
            except KeyboardInterrupt:
                self.logger.debug("[Task-{thread}] Pulling of '{pull}' hit a keyboard interrupt".format(
                    thread=self.get_ident(),
                    pull=self.task.pull.instance
                ))
            except:   # pylint: disable=broad-except
                # Bad thing... Pulling exited with exception
                import traceback
                self.logger.error("[Task-{thread}] Pulling of '{pull}' raised an error\n{error}".format(
                    thread=self.get_ident(),
                    pull=self.task.pull.instance,
                    error=traceback.format_exc()
                ))
            finally:
                if not self.stopped.is_set():
                    directive = self.retry_handler.handle_error()
                    if directive.abort:
                        self.logger.error("[Task-{thread}] Pulling of '{pull}' exited due to retry limitation".format(
                            thread=self.get_ident(),
                            pull=self.task.pull.instance,
                        ))
                        self.stopped.set()
                    else:
                        self._sleep(directive.wait_for)

    def stop(self):
        self.logger.info("[Task-{thread}] Got stopping signal: '{task}'".format(
            thread=self.get_ident(),
            task=self.task.name
        ))
        self._assert_runner()
        self.stopped.set()
        self.task.pull.instance.stop()


@auto_str(__repr__=True)
class StoppableWorker(Loggable):
    """
    Base implementation of a worker that processes fetches items from the queue and delegates it to a push for
    further execution. By default threading is used.

    To stop the worker you should put the `stop_working_item` on the queue.

    For other implementations you have basically to override / adapt:
    * get_ident() -> Some unique identifier
    * start() -> Starts the worker. Start is async and will not block the current execution.
    * join(timeout=...) -> Wait for the worker to finish. Will block!
    * is_alive() -> Checks if the worker is currently running
    * terminate() -> Terminate the worker. Will only be called when the worker does not stop after receiving the
                     `stop_working_item`.
    """
    def __init__(self, queue, stop_working_item):
        """

        Args:
            queue: Queue to fetch processable items from. Should provide `get()` method.
            stop_working_item: Stop the worker when this item hits the queue.
        """
        self.queue = queue
        self.stop_working_item = stop_working_item
        self._worker = None

    @staticmethod
    def get_ident():
        return threading.get_ident()

    def start(self):
        if self._worker:
            raise RuntimeError("Worker is already started and cannot restart...")
        self._worker = threading.Thread(target=self._process_queue)
        self._worker.start()

    def join(self, timeout=None):
        self._assert_runner()
        self._worker.join(timeout=timeout)

    def is_alive(self):
        self._assert_runner()
        return self._worker.is_alive()

    def terminate(self):
        self.logger.warn("Method terminate() on basic StoppableWorker is not supported. The thread will NOT terminate.")

    def _assert_runner(self):
        if not self._worker:
            raise RuntimeError("Runner is is not started")

    def _process_queue(self):
        while True:
            try:
                payload = self.queue.get()
                if payload is self.stop_working_item:
                    self.logger.info("[Worker-{thread}] Got stopping signal".format(
                        thread=threading.get_ident()))
                    # Notify other worker as well
                    self.queue.put(self.stop_working_item)
                    break
                try:
                    # We assume payload is actual payload, push
                    payload, push = payload
                    PushExecutor().execute(
                        id=threading.get_ident(),
                        payload=payload,
                        push=push,
                        result_callback=lambda res, dep: self.queue.put((res, dep))
                    )
                finally:
                    # self.queue.task_done()
                    pass
            except KeyboardInterrupt:
                pass
            except:  # pylint: disable=broad-except
                import traceback
                self.logger.error("\n{}".format(traceback.format_exc()))


@auto_str_ignore(ignore_list=["stop_working_item", "queue", "shutdown", "runner", "worker"])
class ParallelEngine(Engine):
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

    def _make_queue(self):
        return Queue()

    def _make_shutdown_event(self):
        # We might run the Engine in an isolated process. So the multiprocessing.Event() is better suited.
        return multiprocessing.Event()

    def _run_queue_worker(self):
        n_worker = self.queue_worker
        for i in range(n_worker):
            t = self._make_worker()
            t.start()
            self.logger.info("[Worker-{thread}] Started ({i}/{cnt})".format(
                thread=t.get_ident(), i=i + 1, cnt=n_worker))
            self.worker.append(t)

    def _run_tasks(self, tasks):
        for task_name, task in tasks.items():
            t = self._make_runner(task, copy.deepcopy(self.retry_handler))
            t.start()
            self.logger.info("[Task-{thread}] Started for task '{task}'".format(thread=t.get_ident(), task=task.name))
            self.runner.append(t)

    def _stop_runner(self):
        for runner in self.runner:
            self.logger.debug("Stopping runner: {}".format(runner))
            runner.stop()

    def _stop_worker(self):
        self.logger.debug("Pushing stop_working_item on queue")
        self.queue.put(self.stop_working_item)

    def _stop_all(self):
        self._stop_runner()
        self._stop_worker()

    def _wait_for_all(self):
        for t in self.runner + self.worker:
            t.join(timeout=self.stop_timeout)
            if t.is_alive():
                self.logger.warn("{} did not respond to stop command. Terminating...".format(t))
                t.terminate()

    def _run(self, tasks: TaskSet):
        for _, t in tasks.items():
            if not isinstance(t, Task):
                raise TypeError("All items of argument 'tasks' are expected to be a 'Task' instance")

        self._run_queue_worker()
        self._run_tasks(tasks)
        try:
            while not self.shutdown.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        self.logger.debug("Exited control loop. Stopping all threads gracefully")
        self._stop_all()
        self._wait_for_all()

    def _stop(self):
        self.shutdown.set()
