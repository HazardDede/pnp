"""Configuration handling in json/yaml files."""
import os
from typing import Any

from box import Box

from pnp.config._base import Configuration
from pnp.config.yaml_ import YamlConfigLoader
from pnp.models import PullModel


# Available configuration file types and their associated loader
_LOADER = {
    '.yaml': YamlConfigLoader,
    '.json': YamlConfigLoader
}


def load_config(config_path: str) -> Configuration:
    """Load the specified config"""
    if not os.path.isfile(config_path):
        raise FileNotFoundError("Configuration file '{}' not found".format(config_path))

    _, ext = os.path.splitext(config_path)
    loader_clazz = _LOADER.get(ext.lower())
    if not loader_clazz:
        raise RuntimeError(
            "No configuration loader is able to load a '*{}' configuration file".format(ext)
        )
    return loader_clazz(config_path).load_config()


def load_pull_from_snippet(snippet: Any, name: str, **extra: Any) -> PullModel:
    """Loads a pull from a snippet."""
    from pnp.config.yaml_ import Schemas, _mk_pull
    pull_config = Schemas.Pull.validate(snippet)
    return _mk_pull(Box({'name': name, 'pull': pull_config}), **extra)
