from importlib import import_module

from argresolver import EnvironmentResolver

from ..utils import Loggable, auto_str


class PluginMeta(type):
    def __new__(meta, name, bases, dct):
        newly = super().__new__(meta, name, bases, dct)
        # Force all __init__ of plugins to be decorated with envargs
        newly.__init__ = EnvironmentResolver()(newly.__init__)
        return newly


@auto_str(__repr__=True)
class Plugin(Loggable, metaclass=PluginMeta):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name


class ClassNotFoundError(Exception):
    pass


class NamespaceNotFoundError(Exception):
    pass


class InvocationError(Exception):
    pass


def load_plugin(plugin_path, **kwargs):
    if not isinstance(plugin_path, str):
        raise ValueError("Argument plugin_path should be a string but is not.")

    k = plugin_path.rfind('.')
    # Namespace = everything before the last '.'
    namespace = plugin_path[:k]
    # Class name = everything after the last '.'
    clazz_name = plugin_path[k + 1:]

    try:
        loaded_module = import_module(namespace)
        clazz = getattr(loaded_module, clazz_name)

        return clazz(**kwargs)
    except AttributeError:
        raise ClassNotFoundError('Class {} was not found in namespace {}'.format(clazz_name, namespace))
    except ImportError:
        raise NamespaceNotFoundError("Namespace '{}' not found".format(namespace))
    except TypeError as e:
        raise InvocationError("Invoked constructor from class '{}' in namespace '{}' failed".format(
            clazz_name, namespace), e)
