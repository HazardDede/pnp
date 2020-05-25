"""Configuration handling in json/yaml files."""

import os
from typing import Any, Optional

from pnp import validator
from pnp.config._base import Configuration, ConfigLoader
from pnp.config._yaml import YamlConfigLoader
from pnp.models import PullModel

# Available config loader
_LOADER = [YamlConfigLoader]


# Available configuration file types and their associated loader
_EXT_LOADER_MAP = {
    ext: clazz for clazz in _LOADER for ext in clazz.supported_extensions()
}


# Global variable: Which loader was used to load the config
_LOADER_USED = None  # type: Optional[ConfigLoader]


def load_config(config_path: str) -> Configuration:
    """Load the specified config by using a compatible `ConfigLoader`."""
    global _LOADER_USED  # pylint: disable=global-statement

    validator.is_file(config_path=config_path)

    _, ext = os.path.splitext(config_path)
    loader_clazz = _EXT_LOADER_MAP.get(ext.lower().lstrip('.'))
    if not loader_clazz:
        raise RuntimeError(
            "No configuration loader is able to load a '*{}' configuration file".format(ext)
        )
    _LOADER_USED = loader_clazz()
    return _LOADER_USED.load_config(config_path)


def load_pull_from_snippet(snippet: Any, name: str, **extra: Any) -> PullModel:
    """Loads a pull from a snippet using the same `ConfigLoader` that was initially used
    to load the main configuration."""
    global _LOADER_USED  # pylint: disable=global-statement
    loader = _LOADER_USED if _LOADER_USED else YamlConfigLoader()  # Default loader for testing
    return loader.load_pull_from_snippet(snippet, name, **extra)
