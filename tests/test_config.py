import pytest

from pnp.config import load_config
from .conftest import path_to_config


def test_config_load():
    res = load_config(path_to_config('config.simple.json'))
    assert res[0]['name'] == 'simple'
    assert 'pull' in res[0]
    assert 'pushes' in res[0]


def test_inbound_outbound_backward_compat():
    res = load_config(path_to_config('config.in-out-compat.json'))
    assert res[0]['name'] == 'simple'
    assert 'pull' in res[0]
    assert 'pushes' in res[0]
    assert isinstance(res[0]['pushes'], list)


def test_multiple_outbounds():
    res = load_config(path_to_config('config.multiple-pushes.json'))
    assert res[0]['name'] == 'simple'
    assert 'pull' in res[0]
    assert 'pushes' in res[0]
    assert isinstance(res[0]['pushes'], list)
    assert len(res[0]['pushes']) == 2


@pytest.mark.parametrize("config,cnt_deps", [
    ('config.single-dep.yaml', 1),
    ('config.multi-deps.yaml', 3)
])
def test_push_with_deps(config, cnt_deps):
    res = load_config(path_to_config(config))
    assert res[0]['name'] == 'pytest'
    assert 'pull' in res[0]
    assert 'pushes' in res[0]
    assert isinstance(res[0]['pushes'], list)
    assert len(res[0]['pushes']) == 1
    assert 'deps' in res[0]['pushes'][0]
    assert isinstance(res[0]['pushes'][0]['deps'], list)
    assert len(res[0]['pushes'][0]['deps']) == cnt_deps
