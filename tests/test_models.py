from box import Box

from pnp.models import PullModel, PushModel, tasks_to_str, TaskModel, UDFModel
from pnp.plugins.pull.simple import Repeat
from pnp.plugins.push.simple import Echo


def test_mk_pull():
    input = {
        'name': 'pytest',
        'pull': {
            'plugin': 'pnp.plugins.pull.simple.Repeat',
            'args': {'repeat': 'hello', 'wait': 1.0}
        }
    }
    res = TaskModel.mk_pull(Box(input))

    assert isinstance(res, PullModel)
    assert isinstance(res.instance, Repeat)
    assert res.instance.name == 'pytest_pull'
    assert res.instance.repeat == 'hello'
    assert res.instance.interval == 1.0


def test_mk_push():
    input = {
        'name': 'pytest',
        'pushes': [{
            'plugin': 'pnp.plugins.push.simple.Echo',
            'selector': 'blub',
            'args': {},
            'deps': [
                {'plugin': 'pnp.plugins.push.simple.Echo', 'selector': None, 'args': {}, 'deps': []}
            ]
        }]
    }
    res = TaskModel.mk_push(Box(input))

    assert isinstance(res, list)
    assert len(res) == 1
    push = res[0]
    assert isinstance(push, PushModel)
    assert isinstance(push.instance, Echo)
    assert push.instance.name == 'pytest_push_0'
    assert push.selector == 'blub'
    assert len(push.deps) == 1
    dep = push.deps[0]
    assert isinstance(dep, PushModel)
    assert isinstance(dep.instance, Echo)
    assert dep.instance.name == 'pytest_push_0_0'
    assert dep.selector is None


def test_mk_task():
    input = {
        'name': 'pytest',
        'pull': {
            'plugin': 'pnp.plugins.pull.simple.Repeat',
            'args': {'repeat': 'hello', 'wait': 1.0}
        },
        'pushes': [{
            'plugin': 'pnp.plugins.push.simple.Echo',
            'selector': 'blub',
            'args': {},
            'deps': [
                {'plugin': 'pnp.plugins.push.simple.Echo', 'selector': None, 'args': {}, 'deps': []}
            ]
        }]
    }
    res = TaskModel.from_dict(input)

    assert isinstance(res, TaskModel)


def test_mk_udf():
    input = [{
        'name': 'count0',
        'plugin': 'pnp.plugins.udf.simple.Counter',
        'args': None
    },
    {
        'name': 'count5',
        'plugin': 'pnp.plugins.udf.simple.Counter',
        'args': {'init': 5}
    },
    {
        'name': 'my_str',
        'plugin': 'str'
    }]
    res = [UDFModel.from_config(item) for item in input]

    assert len(res) == 3

    count0 = res[0]
    assert count0.name == 'count0'
    assert count0.callable() == 0

    count5 = res[1]
    assert count5.name == 'count5'
    assert count5.callable() == 5
    assert count5.callable() == 6

    my_str = res[2]
    assert my_str.name == 'my_str'
    assert my_str.callable(5) == '5'


def test_task_to_str_for_smoke():
    tasks_to_str({'pytest':
        TaskModel(
            name="pytest",
            pull=PullModel(instance=Repeat(name='pytest_pul', repeat='hello')),
            pushes=[PushModel(instance=Echo(name='pytest_push'), selector=None, deps=[], unwrap=False)]
        )
    })
