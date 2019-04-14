"""Engine implementation using multiprocessing."""

import multiprocessing as proc
import os
from typing import cast

from .parallel import (StoppableRunner, StoppableWorker, ParallelEngine, RetryHandler,
                       QueuePutGet, StopSignal)
from ..models import TaskModel


class ProcessStoppableRunner(StoppableRunner):
    """Runner implementation using multiprocessing thread-like interface."""
    @staticmethod
    def _make_shutdown_event() -> StopSignal:
        return proc.Event()

    @staticmethod
    def get_ident() -> str:
        return str(os.getppid())

    def start(self) -> None:
        if self._runner:
            raise RuntimeError("Runner is already started and cannot restart...")
        self._runner = proc.Process(target=self._start_pull)
        self._runner.start()

    def terminate(self) -> None:
        self._assert_runner()
        self._runner.terminate()  # type: ignore


class ProcessWorker(StoppableWorker):
    """Worker implementation using multiprocessing thread-like interface."""
    @staticmethod
    def get_ident() -> str:
        return str(os.getppid())

    def start(self) -> None:
        if self._worker:
            raise RuntimeError("Worker is already started and cannot restart...")
        self._worker = proc.Process(target=self._process_queue)
        self._worker.start()

    def terminate(self) -> None:
        self._worker.terminate()  # type: ignore


class ProcessEngine(ParallelEngine):
    """Engine implementation using multiprocessing thread-like interface."""
    def _make_worker(self) -> ProcessWorker:
        return ProcessWorker(self.queue, self.stop_working_item)

    def _make_runner(self, task: TaskModel, retry_handler: RetryHandler) -> ProcessStoppableRunner:
        return ProcessStoppableRunner(task, self.queue, retry_handler=retry_handler)

    def _make_queue(self) -> QueuePutGet:
        return cast(QueuePutGet, proc.Queue())

    def _make_shutdown_event(self) -> StopSignal:
        return proc.Event()

    def _stop_worker(self) -> None:
        # We do not use the stop_working_item here... We ungentle terminate the worker
        for worker in self.worker:
            self.logger.debug("Terminating worker: %s", worker)
            worker.terminate()
