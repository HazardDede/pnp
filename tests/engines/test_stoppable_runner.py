import time
from queue import Queue

from pnp import models
from pnp.engines import SimpleRetryHandler, AdvancedRetryHandler
from pnp.engines import parallel as te
from pnp.plugins import pull
from pnp.plugins.pull import simple as pull_simpe
from pnp.plugins.push import simple as push_simple


class ErroneousPullMock(pull.PullBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_count = 0

    def pull(self):
        self.call_count += 1
        raise ValueError("Something went wrong. Once again...")


class NopPullMock(pull.PullBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_count = 0

    def pull(self):
        self.call_count += 1


def test_runner_for_smoke():
    queue = Queue()
    task = models.Task(
        name='pytest_task',
        pull=models.Pull(instance=pull_simpe.Count(name='pytest_pull', wait=0.5)),
        pushes=[models.Push(instance=push_simple.Echo(name='pytest_push'), selector=None, deps=[])]
    )
    dut = te.StoppableRunner(task, queue, SimpleRetryHandler())
    dut.daemon = True
    dut.start()
    time.sleep(1)
    dut.stop()
    dut.join(timeout=1)
    if dut.is_alive():
        assert False

    assert queue.qsize() >= 2


def test_runner_for_retries_on_error():
    def helper_runner(pull, sleep, max_retries):
        queue = Queue()
        task = models.Task(
            name='pytest_task',
            pull=models.Pull(instance=pull),
            pushes=[models.Push(instance=push_simple.Echo(name='pytest_push'), selector=None, deps=[])]
        )
        dut = te.StoppableRunner(task, queue, AdvancedRetryHandler(retry_wait=1, max_retries=max_retries))
        dut.daemon = True
        dut.start()
        time.sleep(sleep)
        dut.stop()
        dut.join(timeout=1)
        if dut.is_alive():
            assert False
        return pull.call_count

    assert helper_runner(ErroneousPullMock(name='pytest_pull'), 1.5, 0) == 1  # Just single pull
    assert helper_runner(ErroneousPullMock(name='pytest_pull'), 2.5, 2) == 3  # Retry two times
    assert helper_runner(NopPullMock(name='pytest_pull'), 1.5, 0) == 1
    assert helper_runner(NopPullMock(name='pytest_pull'), 2.5, 2) == 3
    assert helper_runner(NopPullMock(name='pytest_pull'), 5.2, -1) >= 5  # No retry limitation

