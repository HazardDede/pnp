"""Basic stuff for plugins (pull, push, udf)."""
import logging
from importlib import import_module
from typing import Any, Tuple, Optional, Union, cast, Callable

from pnp import validator
from pnp.utils import auto_str, auto_str_ignore


class InstallOptionalExtraError(ImportError):
    """Is raised when an optional extra is not installed, but a plugin requires it."""
    def __init__(self, extra_name: str):
        super().__init__("You have to install extra '{}' to use this plugin".format(extra_name))


def load_optional_module(namespace: str, extra: str) -> Any:
    """Load an optional module. If the module does not exist an `InstallOptionalExtraError` is
    raised."""
    try:
        return import_module(namespace)
    except ImportError:
        raise InstallOptionalExtraError(extra) from None


class PluginStoppedError(RuntimeError):
    """Is raised when a operation is canceled / refused because the plugin has stopped."""


class PluginLogAdapter(logging.LoggerAdapter):
    """Logging adapter for plugin classes. Will put the name of the plugin in front of the
    message."""
    def __init__(self, logger: logging.Logger, prefix: str):
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg: str, kwargs: Any) -> Tuple[str, Any]:
        return '[{prefix}] {message}'.format(prefix=self.prefix, message=msg), kwargs


@auto_str(__repr__=True)
@auto_str_ignore(['_base_path'])
class Plugin:
    """Base class for a plugin."""

    def __init__(self, name: str, base_path: Optional[str] = None, **kwargs: Any):  # pylint: disable=unused-argument
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
    def base_path(self) -> str:
        """Return the base path of the plugin."""
        # Base path is whether injected (most probably were the loaded config is located
        if self._base_path is None:
            # ... or the current working directory
            import os
            return os.getcwd()
        return self._base_path

    @property
    def logger(self) -> logging.Logger:
        """Return the logger of this instance."""
        component = "{}.{}".format(type(self).__module__, type(self).__name__)
        logger = logging.getLogger(component)
        return cast(logging.Logger, PluginLogAdapter(logger, self.name))


class ClassNotFoundError(Exception):
    """Is raised when the specified class of a plugin is not found."""


class NamespaceNotFoundError(Exception):
    """Is raised when the namespace of a class is not found."""


class InvocationError(Exception):
    """Is raised when the invocation (creation) of the plugin failed."""


class PluginTypeError(Exception):
    """Is raised when the plugin does not meet the requested plugin type or is no plugin at all."""


def load_plugin(plugin_path: str, plugin_type: Union[type, str], instantiate: bool = True,
                **kwargs: Any) -> Union[Plugin, Callable[..., Any]]:
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
    validator.is_instance(str, plugin_path=plugin_path)
    validator.is_instance(type, str, plugin_type=plugin_type)
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
            if not issubclass(clazz, cast(type, plugin_type)):
                raise PluginTypeError(
                    "The plugin is requested to inherit from '{}', but it does not."
                    .format(plugin_type)
                )

        return cast(Plugin, clazz(**kwargs)) if instantiate else cast(Callable[..., Any], clazz)
    except AttributeError:
        raise ClassNotFoundError('Class {} was not found in namespace {}'
                                 .format(clazz_name, namespace)) from None
    except ImportError:
        raise NamespaceNotFoundError("Namespace '{}' not found".format(namespace)) from None
    except TypeError as terr:
        raise InvocationError("Invoked constructor from class '{}' in namespace '{}' failed"
                              .format(clazz_name, namespace)) from terr
