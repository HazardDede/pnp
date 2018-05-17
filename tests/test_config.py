from .context import pnp
from .conftest import path_to_config


def test_config_load():
    res = pnp.config.load_config(path_to_config('config.simple.json'))
    assert res[0]['name'] == 'simple'
    assert 'inbound' in res[0]
    assert 'outbound' in res[0]


def test_inbound_outbound_backward_compat():
    res = pnp.config.load_config(path_to_config('config.in-out-compat.json'))
    assert res[0]['name'] == 'simple'
    assert 'inbound' in res[0]
    assert 'outbound' in res[0]
    assert isinstance(res[0]['outbound'], dict)


def test_multiple_outbounds():
    res = pnp.config.load_config(path_to_config('config.multiple-pushes.json'))
    assert res[0]['name'] == 'simple'
    assert 'inbound' in res[0]
    assert 'outbound' in res[0]
    assert isinstance(res[0]['outbound'], list)
    assert len(res[0]['outbound']) == 2
