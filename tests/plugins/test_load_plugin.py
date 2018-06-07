import pytest

from pnp.plugins import load_plugin, InvocationError, NamespaceNotFoundError, ClassNotFoundError
from pnp.plugins.pull.simple import Repeat


def test_load_plugin():
    plugin = load_plugin("pnp.plugins.pull.simple.Repeat", name='pytest', repeat="Hello World", wait=1)
    assert plugin is not None
    assert isinstance(plugin, Repeat)
    assert str(plugin) == "Repeat(name='pytest', repeat='Hello World', wait=1.0)"


def test_load_plugin_with_invalid_plugins():
    with pytest.raises(ValueError):
        load_plugin(object())
    with pytest.raises(ValueError):
        load_plugin(None)
    with pytest.raises(ValueError):
        load_plugin(1)


def test_load_plugin_wo_required_args():
    with pytest.raises(InvocationError):
        load_plugin("pnp.plugins.pull.simple.Repeat")


def test_load_plugin_with_unknown_package():
    with pytest.raises(NamespaceNotFoundError):
        load_plugin("unknown_namespace.Repeat")


def test_load_plugin_with_unknown_class():
    with pytest.raises(ClassNotFoundError):
        load_plugin("pnp.plugins.pull.simple.Unknown")
