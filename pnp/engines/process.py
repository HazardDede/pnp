import multiprocessing as proc
import os

from .parallel import StoppableRunner, StoppableWorker, ParallelEngine


class ProcessStoppableRunner(StoppableRunner):
    """Runner implementation using multiprocessing thread-like interface."""
    @staticmethod
    def _make_shutdown_event():
        return proc.Event()

    @staticmethod
    def get_ident():
        return os.getppid()

    def start(self):
        if self._runner:
            raise RuntimeError("Runner is already started and cannot restart...")
        self._runner = proc.Process(target=self._start_pull)
        self._runner.start()

    def terminate(self):
        self._assert_runner()
        self._runner.terminate()


class ProcessWorker(StoppableWorker):
    """Worker implementation using multiprocessing thread-like interface."""
    @staticmethod
    def get_ident():
        return os.getppid()

    def start(self):
        if self._worker:
            raise RuntimeError("Worker is already started and cannot restart...")
        self._worker = proc.Process(target=self._process_queue)
        self._worker.start()

    def terminate(self):
        self._worker.terminate()


class ProcessEngine(ParallelEngine):
    """Engine implementation using multiprocessing thread-like interface."""
    def _make_worker(self):
        return ProcessWorker(self.queue, self.stop_working_item)

    def _make_runner(self, task, retry_handler):
        return ProcessStoppableRunner(task, self.queue, retry_handler=retry_handler)

    def _make_queue(self):
        return proc.Queue()

    def _make_shutdown_event(self):
        return proc.Event()

    def _stop_worker(self):
        # We do not use the stop_working_item here... We ungentle terminate the worker
        for worker in self.worker:
            self.logger.debug("Terminating worker: {}".format(worker))
            worker.terminate()
