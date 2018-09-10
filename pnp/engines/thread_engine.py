import threading
import time
from datetime import datetime
from queue import Queue
from threading import Thread

from .general import Engine, PushExecutor
from ..models import Task, TaskSet
from ..utils import Loggable


class StoppableRunner(Thread, Loggable):
    def __init__(self, task, queue, retry_wait=60, max_retries=3, reset_retry_threshold=60):
        if not isinstance(task, Task):
            raise TypeError("Argument 'task' is expected to be a 'Task' instance, but is {}".format(type(task)))
        self.task = task
        self.queue = queue
        self.retry_wait = int(retry_wait)  # in seconds
        self.stopped = threading.Event()
        self.max_retries = int(max_retries) if max_retries is not None else None
        self.reset_retry_threshold = reset_retry_threshold  # Reset retry_count after x seconds of successful running
        super().__init__(target=self._start_pull)

    def _eval_retry(self, retry_count):
        if self.max_retries is None or self.max_retries < 0:
            return True
        return retry_count <= self.max_retries

    def _start_pull(self):
        retry_count = 0
        last_error = None

        def on_payload(plugin, payload):
            # A task / inbound might have multiple pushes / outbounds associated
            for push in self.task.pushes:
                self.logger.debug("[Task-{thread}] Queing item '{item}' for push '{push}'".format(
                    thread=threading.get_ident(),
                    item=payload,
                    push=push
                ))
                # We do not evaluate the selector here. We let this handle the worker process. why?
                # Cause the selector might take some time... and we do not need a try... catch... here
                # Much can go wrong with the selector, if it does it will only cause issues with a single push
                self.queue.put((payload, push))

        def handle_error():
            if last_error is None:
                # Inital value -> no retries so far, the next is 1
                new_retry_count = 1
            elif (datetime.now() - last_error).total_seconds() > self.reset_retry_threshold:
                # Reset retry count because threshold has reached, next try is 1
                new_retry_count = 1
            else:
                # Count the retry accordingly
                new_retry_count = retry_count + 1

            # We don't have to wait if the given max_retries threshold is already reached
            if self._eval_retry(new_retry_count):
                # We couldn't just easily call time.sleep(self, retry_wait), cause we cannot react on the stopping
                # signal. So have to manually sleep in 0.5 second steps and check for stopping signal
                for _ in range(self.retry_wait * 2):
                    if self.stopped.is_set():
                        break
                    time.sleep(0.5)

            # We use this to see how long the new pull lasted
            new_last_error = datetime.now()

            return new_last_error, new_retry_count

        self.task.pull.instance.on_payload = on_payload

        while not self.stopped.is_set() and self._eval_retry(retry_count):
            try:
                self.task.pull.instance.pull()
                if not self.stopped.is_set():
                    # Bad thing... Pulling exited unexpectedly
                    self.logger.error("[Task-{thread}] Pulling of '{pull}' exited unexpectedly".format(
                        thread=threading.get_ident(),
                        pull=self.task.pull.instance,
                    ))
                    last_error, retry_count = handle_error()
            except:
                # Bad thing... Pulling exited with exception
                import traceback
                self.logger.error("[Task-{thread}] Pulling of '{pull}' raised an error\n{error}".format(
                    thread=threading.get_ident(),
                    pull=self.task.pull.instance,
                    error=traceback.format_exc()
                ))
                last_error, retry_count = handle_error()

        if not self.stopped.is_set():
            self.logger.error("[Task-{thread}] Pulling of '{pull}' exited due to retry limitation".format(
                thread=threading.get_ident(),
                pull=self.task.pull.instance,
            ))

    def stop(self):
        self.logger.info("[Task-{thread}] Got stopping signal: '{task}'".format(
            thread=threading.get_ident(),
            task=self.task.name
        ))
        self.stopped.set()
        self.task.pull.instance.stop()


class StoppableWorker(Thread, Loggable):
    def __init__(self, queue, stop_working_item):
        self.queue = queue
        self.stop_working_item = stop_working_item
        super().__init__(target=self._process_queue)

    def _process_queue(self):
        while True:
            try:
                payload = self.queue.get()
                if payload is self.stop_working_item:
                    self.logger.info("[Worker-{thread}] Got stopping signal".format(
                        thread=threading.get_ident()))
                    self.queue.put(self.stop_working_item)
                    break
                try:
                    # We assume payload is actual payload, push
                    payload, push = payload
                    PushExecutor().execute(
                        id=threading.get_ident(),
                        payload=payload,
                        push=push,
                        # result_callback=lambda res, dep: self.queue.put((res, dep))
                    )
                finally:
                    self.queue.task_done()
            except:  # pylint: disable=broad-except
                import traceback
                self.logger.error("\n{}".format(traceback.format_exc()))


class ThreadEngine(Engine):
    def __init__(self, queue_worker=3):
        super().__init__()
        self.queue_worker = max(int(queue_worker), 1)
        self.stop_working_item = object()
        self.queue = Queue()
        self.runner = []
        self.worker = []
        self.shutdown = threading.Event()

    def _run_queue_worker(self):
        n_worker = self.queue_worker
        for i in range(n_worker):
            t = StoppableWorker(self.queue, self.stop_working_item)
            t.start()
            self.logger.info("[Worker-{thread}] Started ({i}/{cnt})".format(thread=t.ident, i=i + 1, cnt=n_worker))
            self.worker.append(t)

    def _run_tasks(self, tasks):
        for task_name, task in tasks.items():
            t = StoppableRunner(task, self.queue)
            t.start()
            self.logger.info("[Task-{thread}] Started for task '{task}'".format(thread=t.ident, task=task.name))
            self.runner.append(t)

    def _stop_all(self):
        for runner in self.runner:
            runner.stop()
        self.queue.put(self.stop_working_item)

    def _run(self, tasks: TaskSet):
        for _, t in tasks.items():
            if not isinstance(t, Task):
                raise TypeError("All items of argument 'tasks' are expected to be a 'Task' instance")

        self._run_queue_worker()
        self._run_tasks(tasks)
        while not self.shutdown.is_set():
            time.sleep(1)
        self.logger.debug("Exited control loop. Stopping all threads gracefully")
        self._stop_all()
        for t in self.runner + self.worker:
            t.join()

    def _stop(self):
        self.shutdown.set()
