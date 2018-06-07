from .conftest import path_to_config
from .context import pnp


def test_config_load():
    res = pnp.config.load_config(path_to_config('config.simple.json'))
    assert res[0]['name'] == 'simple'
    assert 'pull' in res[0]
    assert 'pushes' in res[0]


def test_inbound_outbound_backward_compat():
    res = pnp.config.load_config(path_to_config('config.in-out-compat.json'))
    assert res[0]['name'] == 'simple'
    assert 'pull' in res[0]
    assert 'pushes' in res[0]
    assert isinstance(res[0]['pushes'], list)


def test_multiple_outbounds():
    res = pnp.config.load_config(path_to_config('config.multiple-pushes.json'))
    assert res[0]['name'] == 'simple'
    assert 'pull' in res[0]
    assert 'pushes' in res[0]
    assert isinstance(res[0]['pushes'], list)
    assert len(res[0]['pushes']) == 2
