import time
from queue import Queue

from .context import pnp

from pnp import app, models
from pnp.plugins.pull import simple as pull_simple
from pnp.plugins.push import simple as push_simple


def test_runner_for_smoke():
    queue = Queue()
    task = models.Task(
        name='pytest_task',
        pull=models.Pull(instance=pull_simple.Count(name='pytest_pull', wait=0.5)),
        pushes=[models.Push(instance=push_simple.Echo(name='pytest_push'), selector=None)]
    )
    dut = app.StoppableRunner(task, queue)
    dut.daemon = True
    dut.start()
    time.sleep(1)
    dut.stop()
    dut.join(timeout=1)
    if dut.is_alive():
        assert False

    assert queue.qsize() >= 2
