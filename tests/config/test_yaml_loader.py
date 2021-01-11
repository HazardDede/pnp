import pytest
from box import Box

from pnp.config._yaml import _mk_pull, _mk_push, _mk_udf, YamlConfigLoader
from pnp.engines import SimpleRetryHandler, AsyncEngine
from pnp.models import PullModel, PushModel, APIModel
from pnp.plugins.pull.simple import Repeat, Count
from pnp.plugins.push.simple import Echo
from tests.conftest import path_to_config


def test_mk_pull():
    input = {
        'name': 'pytest',
        'pull': {
            'plugin': 'pnp.plugins.pull.simple.Repeat',
            'args': {'repeat': 'hello', 'wait': 1.0}
        }
    }
    res = _mk_pull(Box(input))

    assert isinstance(res, PullModel)
    assert isinstance(res.instance, Repeat)
    assert res.instance.name == 'pytest_pull'
    assert res.instance.repeat == 'hello'
    assert res.instance.interval == 1.0


def test_mk_push():
    input = {
        'name': 'pytest',
        'push': [{
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


def test_mk_udf():
    input = [{
        'name': 'count0',
        'plugin': 'pnp.plugins.udf.simple.Counter',
        'args': None
    }, {
        'name': 'count5',
        'plugin': 'pnp.plugins.udf.simple.Counter',
        'args': {'init': 5}
    }, {
        'name': 'my_str',
        'plugin': 'str'
    }]
    res = [_mk_udf(item) for item in input]

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


def test_load_config():
    dut = YamlConfigLoader()
    config = dut.load_config(path_to_config('config.simple.json'))

    assert config.engine is None
    assert list(config.tasks.keys()) == ['simple']

    simple_task = config.tasks['simple']
    assert isinstance(simple_task.pull.instance, Count)
    assert len(simple_task.pushes) == 1
    assert isinstance(simple_task.pushes[0].instance, Echo)


def test_load_config_multiple_pushes():
    dut = YamlConfigLoader()
    config = dut.load_config(path_to_config('config.multiple-pushes.json'))

    assert config.engine is None
    assert list(config.tasks.keys()) == ['simple']

    simple_task = config.tasks['simple']
    assert isinstance(simple_task.pull.instance, Count)
    assert len(simple_task.pushes) == 2
    assert isinstance(simple_task.pushes[0].instance, Echo)
    assert isinstance(simple_task.pushes[1].instance, Echo)


@pytest.mark.parametrize("config,cnt_deps", [
    ('config.single-dep.yaml', 1),
    ('config.multi-deps.yaml', 3)
])
def test_load_config_push_with_deps(config, cnt_deps):
    dut = YamlConfigLoader()
    config = dut.load_config(path_to_config(config))
    assert list(config.tasks.keys()) == ['pytest']
    simple_task = config.tasks['pytest']
    assert isinstance(simple_task.pull.instance, Count)
    assert len(simple_task.pushes) == 1
    assert isinstance(simple_task.pushes[0].instance, Echo)

    assert len(simple_task.pushes[0].deps) == cnt_deps
    for dependency in simple_task.pushes[0].deps:
        assert isinstance(dependency, PushModel)
        assert isinstance(dependency.instance, Echo)


def test_load_config_with_engine():
    dut = YamlConfigLoader()
    config = dut.load_config(path_to_config('config.engine.yaml'))

    engine = config.engine
    tasks = config.tasks
    assert engine is not None
    assert isinstance(engine, AsyncEngine)
    assert isinstance(engine.retry_handler, SimpleRetryHandler)
    assert engine.retry_handler.retry_wait == 60

    assert list(tasks.keys()) == ['pytest']
    simple_task = tasks['pytest']
    assert simple_task.name == 'pytest'


def test_supported_extensions():
    assert YamlConfigLoader.supported_extensions() == ['json', 'yaml', 'yml']


def test_api():
    dut = YamlConfigLoader()

    config = dut.load_config(path_to_config('config.api.none.yaml'))
    assert config.api is None

    config = dut.load_config(path_to_config('config.api.min.yaml'))
    assert config.api == APIModel(port=12345, enable_metrics=False)

    config = dut.load_config(path_to_config('config.api.max.yaml'))
    assert config.api == APIModel(port=23456, enable_metrics=True)
