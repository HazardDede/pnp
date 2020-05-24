"""Contains base classes for config parsers."""
from abc import abstractmethod
from functools import partial
from typing import Optional, Iterable, Any

import attr

from pnp.engines import Engine
from pnp.models import TaskSet, UDFModel, TaskModel, PullModel, APIModel
from pnp.validator import attrs_validator_dict_items, attrs_validate_list_items


@attr.s
class Configuration:
    """Represents a parsed, instantiated and valid configuration."""
    api = attr.ib(
        validator=attr.validators.instance_of((type(None), APIModel))
    )  # type: Optional[APIModel]

    tasks = attr.ib(
        validator=partial(attrs_validator_dict_items, key_type=str, val_type=TaskModel)
    )  # type: TaskSet

    engine = attr.ib(
        validator=attr.validators.instance_of((type(None), Engine)),
        default=None
    )  # type: Optional[Engine]

    udfs = attr.ib(
        converter=lambda val: val or [],  # type: ignore
        validator=partial(attrs_validate_list_items, item_type=UDFModel),
        default=None
    )  # type: Iterable[UDFModel]


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
