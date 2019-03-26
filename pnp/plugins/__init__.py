"""Basic stuff for plugins (pull, push, udf)."""

import warnings
from importlib import import_module

from argresolver import EnvironmentResolver

from ..utils import Loggable, auto_str, auto_str_ignore
from ..validator import Validator

# https://stackoverflow.com/questions/40845304/  \
# runtimewarning-numpy-dtype-size-changed-may-indicate-binary-incompatibility
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


class InstallOptionalExtraError(ImportError):
    """Is raised when an optional extra is not installed, but a plugin requires it."""
    def __init__(self, extra_name):
        super().__init__("You have to install extra '{}' to use this plugin".format(extra_name))


def load_optional_module(namespace, extra):
    """Load an optional module. If the module does not exist an `InstallOptionalExtraError` is
    raised."""
    try:
        return import_module(namespace)
    except ImportError:
        raise InstallOptionalExtraError(extra)


class PluginMeta(type):
    """Metaclasses for plugins. Hooks up the `argresolver`-package to inject any missing arguments
    at runtime if provided as an environment variable."""
    def __new__(cls, name, bases, dct):
        newly = super().__new__(cls, name, bases, dct)
        # Force all __init__ of plugins to be decorated with envargs
        newly.__init__ = EnvironmentResolver(default_override=True)(newly.__init__)
        return newly


@auto_str(__repr__=True)
@auto_str_ignore(['_base_path'])
class Plugin(Loggable, metaclass=PluginMeta):
    """Base class for a plugin."""

    def __init__(self, name, base_path=None, **kwargs):  # pylint: disable=unused-argument
        """
        Initializer.

        Args:
            name (str): Name of the plugin.
            base_path (str): Base path the plugin should use.
            **kwargs: Additional arguments.
        """
        super().__init__()
        self.name = str(name)
        self._base_path = base_path and str(base_path)

    @property
    def base_path(self):
        """Return the base path of the plugin."""
        # Base path is whether injected (most probably were the loaded config is located
        if self._base_path is None:
            # ... or the current working directory
            import os
            return os.getcwd()
        return self._base_path


class ClassNotFoundError(Exception):
    """Is raised when the specified class of a plugin is not found."""


class NamespaceNotFoundError(Exception):
    """Is raised when the namespace of a class is not found."""


class InvocationError(Exception):
    """Is raised when the invocation (creation) of the plugin failed."""


class PluginTypeError(Exception):
    """Is raised when the plugin does not meet the requested plugin type or is no plugin at all."""


def load_plugin(plugin_path, plugin_type, instantiate=True, **kwargs):
    """
    Loads a plugin by using a fully qualified identifier (<module_path>.<class_name>,
    e.g. pnp.plugins.pull.simple.Repeat).

    Args:
        plugin_path: Fully qualified path to plugin path.
        plugin_type: Base class the plugin has to extend / inherit from.
        instantiate: If True the class will be instantiated by passing the given **kwargs.
            Otherwise the class (not an object) is returned.
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
    Validator.is_instance(type, str, plugin_type=plugin_type)
    if isinstance(plugin_type, str) and plugin_type != 'callable':
        raise ValueError("When 'plugin_type' is str, the only allowed value is callable")

    k = plugin_path.rfind('.')
    if k > -1:
        # Namespace = everything before the last '.'
        namespace = plugin_path[:k]
        # Class name = everything after the last '.'
        clazz_name = plugin_path[k + 1:]
    else:
        namespace = 'builtins'
        clazz_name = plugin_path

    try:
        loaded_module = import_module(namespace)
        clazz = getattr(loaded_module, clazz_name)

        if isinstance(plugin_type, str) and plugin_type == 'callable':
            if not callable(clazz):
                raise PluginTypeError("The plugin is requested to be a callable, but it is not.")
        else:
            if not issubclass(clazz, plugin_type):
                raise PluginTypeError(
                    "The plugin is requested to inherit from '{}', but it does not."
                    .format(plugin_type)
                )

        return clazz(**kwargs) if instantiate else clazz
    except AttributeError:
        raise ClassNotFoundError('Class {} was not found in namespace {}'
                                 .format(clazz_name, namespace))
    except ImportError:
        raise NamespaceNotFoundError("Namespace '{}' not found".format(namespace))
    except TypeError as terr:
        raise InvocationError("Invoked constructor from class '{}' in namespace '{}' failed"
                              .format(clazz_name, namespace)) from terr
