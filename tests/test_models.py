from box import Box

from pnp.models import Pull, _mk_pull, _mk_push, Push, tasks_to_str, Task
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
    res = _mk_pull(Box(input))

    assert isinstance(res, Pull)
    assert isinstance(res.instance, Repeat)
    assert res.instance.name == 'pytest_pull'
    assert res.instance.repeat == 'hello'
    assert res.instance.wait == 1.0


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
    res = _mk_push(Box(input))

    assert isinstance(res, list)
    assert len(res) == 1
    push = res[0]
    assert isinstance(push, Push)
    assert isinstance(push.instance, Echo)
    assert push.instance.name == 'pytest_push_0'
    assert push.selector == 'blub'
    assert len(push.deps) == 1
    dep = push.deps[0]
    assert isinstance(dep, Push)
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
    res = Task.from_dict(input)

    assert isinstance(res, Task)


def test_task_to_str_for_smoke():
    tasks_to_str({'pytest':
        Task(
            name="pytest",
            pull=Pull(instance=Repeat(name='pytest_pul', repeat='hello')),
            pushes=[Push(instance=Echo(name='pytest_push'), selector=None, deps=[])]
        )
    })
