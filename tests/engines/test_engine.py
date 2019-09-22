import time
from functools import partial
from threading import Thread

import pytest

from pnp.engines import NoRetryHandler
from pnp.engines.async_ import AsyncEngine
from pnp.engines.process import ProcessEngine
from pnp.engines.sequential import SequentialEngine
from pnp.engines.thread import ThreadEngine
from pnp.models import TaskModel, PullModel, PushModel
from pnp.plugins.pull.simple import Count
from pnp.plugins.push.simple import Echo
from . import run_engine


@pytest.mark.parametrize("engine", [
    SequentialEngine(retry_handler=NoRetryHandler()),
    ThreadEngine(retry_handler=NoRetryHandler()),
    ProcessEngine(retry_handler=NoRetryHandler()),
])
def test_engine_for_smoke(engine):
    deps = [PushModel(instance=Echo(name='dep_echo'), selector="payload", deps=[], unwrap=False)]
    tasks = {'pytest': TaskModel(
        name="pytest",
        pull=PullModel(instance=Count(name='count', from_cnt=0, wait=0.5)),
        pushes=[PushModel(instance=Echo(name='echo'), selector=None, deps=deps, unwrap=False)]
    )}
    run_engine(engine, tasks)


def test_async_engine_for_smoke():
    engine = AsyncEngine(retry_handler=NoRetryHandler())
    deps = [PushModel(instance=Echo(name='dep_echo'), selector="payload", deps=[], unwrap=False)]
    tasks = {'pytest': TaskModel(
        name="pytest",
        pull=PullModel(instance=Count(name='count', from_cnt=0, wait=0.5)),
        pushes=[PushModel(instance=Echo(name='echo'), selector=None, deps=deps, unwrap=False)]
    )}
    t = Thread(target=partial(engine.run, tasks=tasks))
    try:
        t.start()
        time.sleep(1)
        engine.stop()
        t.join(timeout=5)
    finally:
        if t.is_alive():
            assert False
