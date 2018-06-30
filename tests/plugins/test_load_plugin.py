import pytest

from pnp.plugins import load_plugin, InvocationError, NamespaceNotFoundError, ClassNotFoundError, PluginTypeError
from pnp.plugins.pull.simple import Repeat
from pnp.plugins.pull import PullBase


def test_load_plugin():
    plugin = load_plugin("pnp.plugins.pull.simple.Repeat", PullBase, name='pytest', repeat="Hello World", wait=1)
    assert plugin is not None
    assert isinstance(plugin, Repeat)
    assert str(plugin) == "Repeat(name='pytest', repeat='Hello World', wait=1.0)"


def test_load_plugin_with_invalid_plugins():
    with pytest.raises(TypeError):
        load_plugin(object(), object)
    with pytest.raises(TypeError):
        load_plugin(None, object)
    with pytest.raises(TypeError):
        load_plugin(1, object)


def test_load_plugin_wo_required_args():
    with pytest.raises(InvocationError):
        load_plugin("pnp.plugins.pull.simple.Repeat", object)


def test_load_plugin_with_unknown_package():
    with pytest.raises(NamespaceNotFoundError):
        load_plugin("unknown_namespace.Repeat", object)


def test_load_plugin_with_unknown_class():
    with pytest.raises(ClassNotFoundError):
        load_plugin("pnp.plugins.pull.simple.Unknown", object)


def test_load_plugin_with_wrong_base_type():
    with pytest.raises(PluginTypeError) as e:
        load_plugin("pnp.plugins.pull.simple.Repeat", str)
    assert "The plugin is requested to inherit from '<class 'str'>', but it does not." in str(e)
