"""pull.gpio for backwards compatibility reasons."""

# pylint: disable=no-name-in-module
from pnp.plugins.pull.io import GPIOWatcher  # type: ignore

Watcher = GPIOWatcher

__all__ = [
    'Watcher'
]
