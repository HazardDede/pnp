from importlib import import_module

from argresolver import EnvironmentResolver

from ..utils import Loggable, auto_str
from ..validator import Validator


class PluginMeta(type):
    def __new__(meta, name, bases, dct):
        newly = super().__new__(meta, name, bases, dct)
        # Force all __init__ of plugins to be decorated with envargs
        newly.__init__ = EnvironmentResolver(default_override=True)(newly.__init__)
        return newly


@auto_str(__repr__=True)
class Plugin(Loggable, metaclass=PluginMeta):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = str(name)


class ClassNotFoundError(Exception):
    pass


class NamespaceNotFoundError(Exception):
    pass


class InvocationError(Exception):
    pass


class PluginTypeError(Exception):
    pass


def load_plugin(plugin_path, plugin_type, **kwargs):
    """
    Loads a plugin by using a fully qualified identifier (<module_path>.<class_name>,
    e.g. pnp.plugins.pull.simple.Repeat).

    Args:
        plugin_path: Fully qualified path to plugin path.
        plugin_type: Base class the plugin has to extend / inherit from.
        **kwargs: Plugin arguments.

    Returns:
        If everything went fine an instantiated plugin is returned.
        Multiple things can go wrong:
        - Module not found (NamespaceNotFoundError)
        - Class not found (ClassNotFoundError)
        - Instantiation error (InvocationError)
        - Wrong plugin base type (PluginTypeError)
    """
    Validator.is_instance(str, plugin_path=plugin_path)
    Validator.is_instance(type, plugin_type=plugin_type)

    k = plugin_path.rfind('.')
    # Namespace = everything before the last '.'
    namespace = plugin_path[:k]
    # Class name = everything after the last '.'
    clazz_name = plugin_path[k + 1:]

    try:
        loaded_module = import_module(namespace)
        clazz = getattr(loaded_module, clazz_name)
        if not issubclass(clazz, plugin_type):
            raise PluginTypeError("The plugin is requested to inherit from '{}', but it does not.".format(plugin_type))

        return clazz(**kwargs)
    except AttributeError:
        raise ClassNotFoundError('Class {} was not found in namespace {}'.format(clazz_name, namespace))
    except ImportError:
        raise NamespaceNotFoundError("Namespace '{}' not found".format(namespace))
    except TypeError as e:
        raise InvocationError("Invoked constructor from class '{}' in namespace '{}' failed".format(
            clazz_name, namespace), e)
