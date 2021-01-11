"""Contains base classes for config parsers."""
from abc import abstractmethod
from typing import Optional, Iterable, Any, List

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from pnp.engines import Engine
from pnp.models import TaskSet, UDFModel, PullModel, APIModel


class Configuration(BaseModel):
    """Represents a parsed, instantiated and valid configuration."""

    # API instance if configured or None
    api: Optional[APIModel]

    # A set of tasks of this configuration
    tasks: TaskSet

    # The engine that is configured; might be None if no engine was specified
    engine: Optional[Engine]

    # The configured udfs. List is empty if no udf is configured
    udfs: List[UDFModel]

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


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
