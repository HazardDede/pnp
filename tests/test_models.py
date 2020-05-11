from pnp.models import PullModel, PushModel, tasks_to_str, TaskModel
from pnp.plugins.pull.simple import Repeat
from pnp.plugins.push.simple import Echo


def test_task_to_str_for_smoke():
    tasks_to_str({'pytest':
        TaskModel(
            name="pytest",
            pull=PullModel(instance=Repeat(name='pytest_pul', repeat='hello')),
            pushes=[PushModel(instance=Echo(name='pytest_push'), selector=None, deps=[], unwrap=False)]
        )
    })
