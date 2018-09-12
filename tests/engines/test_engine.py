import pytest

from pnp.engines import NoRetryHandler
from pnp.engines.process import ProcessEngine
from pnp.engines.sequential import SequentialEngine
from pnp.engines.thread import ThreadEngine
from pnp.models import Task, Pull, Push
from pnp.plugins.pull.simple import Count
from pnp.plugins.push.simple import Echo
from . import run_engine


@pytest.mark.parametrize("engine", [
    SequentialEngine(retry_handler=NoRetryHandler()),
    ThreadEngine(retry_handler=NoRetryHandler()),
    ProcessEngine(retry_handler=NoRetryHandler())
])
def test_engine_for_smoke(engine):
    tasks = {'pytest': Task(
        name="pytest",
        pull=Pull(instance=Count(name='count', from_cnt=0, wait=0.5)),
        pushes=[Push(instance=Echo(name='echo'), selector=None, deps=[])]
    )}
    run_engine(engine, tasks)
