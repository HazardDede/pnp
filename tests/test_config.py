import pytest

from pnp.config import load_config
from pnp.engines import SimpleRetryHandler
from pnp.engines.thread import ThreadEngine
from .conftest import path_to_config


def test_config_load():
    engine, tasks = load_config(path_to_config('config.simple.json'))
    assert engine is None
    assert tasks[0]['name'] == 'simple'
    assert 'pull' in tasks[0]
    assert 'pushes' in tasks[0]


def test_inbound_outbound_backward_compat():
    engine, tasks = load_config(path_to_config('config.in-out-compat.json'))
    assert engine is None
    assert tasks[0]['name'] == 'simple'
    assert 'pull' in tasks[0]
    assert 'pushes' in tasks[0]
    assert isinstance(tasks[0]['pushes'], list)


def test_multiple_outbounds():
    engine, tasks = load_config(path_to_config('config.multiple-pushes.json'))
    assert engine is None
    assert tasks[0]['name'] == 'simple'
    assert 'pull' in tasks[0]
    assert 'pushes' in tasks[0]
    assert isinstance(tasks[0]['pushes'], list)
    assert len(tasks[0]['pushes']) == 2


@pytest.mark.parametrize("config,cnt_deps", [
    ('config.single-dep.yaml', 1),
    ('config.multi-deps.yaml', 3)
])
def test_push_with_deps(config, cnt_deps):
    engine, tasks = load_config(path_to_config(config))
    assert engine is None
    assert tasks[0]['name'] == 'pytest'
    assert 'pull' in tasks[0]
    assert 'pushes' in tasks[0]
    assert isinstance(tasks[0]['pushes'], list)
    assert len(tasks[0]['pushes']) == 1
    assert 'deps' in tasks[0]['pushes'][0]
    assert isinstance(tasks[0]['pushes'][0]['deps'], list)
    assert len(tasks[0]['pushes'][0]['deps']) == cnt_deps


def test_load_config_with_engine():
    engine, tasks = load_config(path_to_config('config.engine.yaml'))
    assert engine is not None
    assert isinstance(engine, ThreadEngine)
    assert engine.queue_worker == 10
    assert isinstance(engine.retry_handler, SimpleRetryHandler)
    assert engine.retry_handler.retry_wait == 60
    assert tasks[0]['name'] == 'pytest'
    assert 'pull' in tasks[0]
    assert 'pushes' in tasks[0]
