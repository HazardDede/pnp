from .context import pnp
from .conftest import path_to_config


def test_config_load():
    res = pnp.config.load_config(path_to_config('config.simple.json'))
    assert res[0]['name'] == 'simple'
    assert 'inbound' in res[0]
    assert 'outbound' in res[0]


def test_inbound_outbound_backward_compat():
    res = pnp.config.load_config(path_to_config('config.simple.in-out.json'))
    assert res[0]['name'] == 'simple'
    assert 'inbound' in res[0]
    assert 'outbound' in res[0]
