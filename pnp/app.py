import signal
import threading
import time
from queue import Queue
from threading import Thread

from .utils import Loggable


class StoppableRunner(Thread, Loggable):
    def __init__(self, task, queue):
        self.task = task
        self.queue = queue
        super().__init__(target=self._start_pull)

    def _start_pull(self):
        def on_payload(plugin, payload):
            self.logger.debug("[Task-{thread}] Queing item '{item}' for outbound '{outbound}'".format(
                thread=threading.get_ident(),
                item=payload,
                outbound=self.task.outbound
            ))
            self.queue.put((payload, self.task.outbound))

        self.task.inbound.on_payload = on_payload
        # TODO: Retry pull (failure count)
        self.task.inbound.pull()

    def stop(self):
        self.logger.info("[Task-{thread}] Got stopping signal: '{task}'".format(
            thread=threading.get_ident(),
            task=self.task.name
        ))
        self.task.inbound.stop()


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
                    payload, outbound = self.queue.get()
                    try:
                        if payload is self.stop_working_item:
                            self.logger.info("[Worker-{thread}] Got stopping signal".format(
                                thread=threading.get_ident()))
                            self.queue.put((self.stop_working_item, None))
                            break
                        self.logger.debug("[Worker-{thread}] Emitting '{payload}' to outbound '{outbound}'".format(
                            thread=threading.get_ident(), payload=payload, outbound=outbound))
                        outbound.push(payload=payload)
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
