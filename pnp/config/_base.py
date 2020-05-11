"""Contains base classes for config parsers."""
from abc import abstractmethod
from typing import Optional, Iterable, Any

import attr

from pnp.engines import Engine
from pnp.models import TaskSet, UDFModel, TaskModel, PullModel


def _validate_tasks(instance: 'Configuration', attrib: Any, val: Any) -> Any:
    _, _ = instance, attrib

    if not isinstance(val, dict):
        raise TypeError(
            "Argument 'tasks' is expected to be a dictionary, but is {}".format(type(val))
        )
    for i, (key, value) in enumerate(val.items()):
        if not isinstance(key, str):
            raise TypeError(
                "Key at {} position is expected to be a str, but is {}".format(i, type(value))
            )
        if not isinstance(value, TaskModel):
            raise TypeError(
                "Value at {} position is expected to be a TaskModel, but is {}".format(
                    i, type(value)
                )
            )
    return val


def _validate_udfs(instance: 'Configuration', attrib: Any, val: Any) -> Any:
    _, _ = instance, attrib

    if val is None:
        return val  # None is ok

    if not isinstance(val, (tuple, list)):
        raise TypeError(
            "Argument 'tasks' is expected to be an iterable, but is {}".format(type(val))
        )
    for i, item in enumerate(val):
        if not isinstance(item, UDFModel):
            raise TypeError(
                "Item value at {} position is expected to be a UDFModel, but is {}".format(
                    i, type(item)
                )
            )
    return val


@attr.s
class Configuration:
    """Represents a parsed, instantiated and valid configuration."""
    tasks = attr.ib(
        validator=_validate_tasks
    )  # type: TaskSet

    engine = attr.ib(
        validator=attr.validators.instance_of((type(None), Engine)),
        default=None
    )  # type: Optional[Engine]

    udfs = attr.ib(
        validator=_validate_udfs,
        default=None
    )  # type: Optional[Iterable[UDFModel]]


class ConfigLoader:
    """Base class / interface for any configuration loader."""

    @classmethod
    def supported_extensions(cls) -> Iterable[str]:
        """Returns an iterable with all supported file extensions."""
        raise NotImplementedError()

    @abstractmethod
    def load_pull_from_snippet(self, snippet: Any, name: str, **extra: Any) -> PullModel:
        """Return a new pull model instantiated from a config snippet.

        Args:
            snippet (Any): The configuration snippet to configure a pull.
            name (str): The name of the pull (if part of the snippet; the config will take
              precedence)
            extra: Any extra arguments to instantiate the pull.

        Return:
            The instantiated pull model.
        """
        raise NotImplementedError()

    @abstractmethod
    def load_config(self, config_file: str) -> Configuration:
        """Load the configuration from the specified config file.

        Args:
            config_file: The config file to load. Which files are supported depends on the loader.

        Return:
            A full-blown / instantiated configuration.
        """
        raise NotImplementedError()
