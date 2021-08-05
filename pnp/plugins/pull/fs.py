"""File system related plugins for backwards compatibility."""

# pylint: disable=no-name-in-module
from pnp.plugins.pull.io import FSSize, FSWatcher  # type: ignore


FileSystemWatcher = FSWatcher
Size = FSSize
