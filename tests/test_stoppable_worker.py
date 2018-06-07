import time
from queue import Queue

from pnp import app, models
from pnp.plugins import push
from pnp.plugins.pull import simple as pull_simple


class PushMock(push.PushBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pushes = list()

    def push(self, payload):
        self.pushes.append(payload)


def test_worker_for_smoke():
    queue = Queue()
    push_instance = PushMock(name='pytest_push')
    task = models.Task(
        name='pytest_task',
        pull=models.Pull(instance=pull_simple.Count(name='pytest_pull', wait=0.5)),
        pushes=[models.Push(instance=push_instance, selector=None, deps=[])]
    )
    # Worker
    stop_item = object()
    worker = app.StoppableWorker(queue, stop_item)
    worker.daemon = True
    worker.start()

    # Runner
    runner = app.StoppableRunner(task, queue)
    runner.daemon = True

    runner.start()
    time.sleep(1)
    runner.stop()
    queue.put(stop_item)

    runner.join(timeout=1)
    if runner.is_alive():
        assert False

    worker.join(timeout=1)
    if worker.is_alive():
        assert False

    assert set(push_instance.pushes) >= {0, 1}
