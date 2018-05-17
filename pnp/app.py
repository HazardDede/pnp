import signal
import threading
import time
from queue import Queue
from threading import Thread

from .models import Task
from .utils import Loggable, safe_eval


class StoppableRunner(Thread, Loggable):
    def __init__(self, task, queue):
        if not isinstance(task, Task):
            raise TypeError("Argument 'task' is expected to be a 'Task' instance, but is {}".format(type(task)))
        self.task = task
        self.queue = queue
        super().__init__(target=self._start_pull)

    def _start_pull(self):
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
                # Much can go wrong with the selector, if will only cause issues with the actual push
                self.queue.put((payload, push))

        self.task.pull.instance.on_payload = on_payload
        # TODO: Retry pull (failure count)
        self.task.pull.instance.pull()

    def stop(self):
        self.logger.info("[Task-{thread}] Got stopping signal: '{task}'".format(
            thread=threading.get_ident(),
            task=self.task.name
        ))
        self.task.pull.instance.stop()


class Application(Loggable):
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.stop_working_item = object()

        self.queue = Queue()
        self.runner = []
        self.worker = []

    def exit_gracefully(self, signum, frame):
        self.logger.info("Got exit signal")
        self.shutdown = True

    def run_queue_worker(self, n_worker=1):
        def process_queue():
            while True:
                try:
                    payload, push = self.queue.get()
                    try:
                        if payload is self.stop_working_item:
                            self.logger.info("[Worker-{thread}] Got stopping signal".format(
                                thread=threading.get_ident()))
                            self.queue.put((self.stop_working_item, None))
                            break
                        if push.selector is not None:
                            self.logger.debug("[Worker-{thread}] Applying '{selector}' to '{payload}'".format(
                                thread=threading.get_ident(), payload=payload, selector=push.selector))
                            payload = safe_eval(push.selector, payload=payload)

                        self.logger.debug("[Worker-{thread}] Emitting '{payload}' to push '{push}'".format(
                            thread=threading.get_ident(), payload=payload, push=push.instance))
                        push.instance.push(payload=payload)
                    finally:
                        self.queue.task_done()
                except:  # pylint: disable=broad-except
                    import traceback
                    self.logger.error("\n{}".format(traceback.format_exc()))

        for i in range(n_worker):
            t = Thread(target=process_queue)
            t.start()
            self.logger.info("[Worker-{thread}] Started ({i}/{cnt})".format(thread=t.ident, i=i + 1, cnt=n_worker))
            self.worker.append(t)

    def run_tasks(self, tasks):
        for task_name, task in tasks.items():
            t = StoppableRunner(task, self.queue)
            t.start()
            self.logger.info("[Task-{thread}] Started for task '{task}'".format(thread=t.ident, task=task.name))
            self.runner.append(t)

    def run(self, tasks):
        for _, t in tasks.items():
            if not isinstance(t, Task):
                raise TypeError("All items of argument 'tasks' are expected to be a 'Task' instance")

        self.run_queue_worker(n_worker=3)
        self.run_tasks(tasks)
        while not self.shutdown:
            time.sleep(1)
        self.logger.debug("Exited control loop. Stopping all threads gracefully")
        self.stop_all()
        for t in self.runner + self.worker:
            t.join()

    def stop_all(self):
        for runner in self.runner:
            runner.stop()
        self.queue.put((self.stop_working_item, None))
