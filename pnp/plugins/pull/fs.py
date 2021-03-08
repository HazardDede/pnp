"""File system related plugins for backwards compatibility."""

# pylint: disable=no-name-in-module
from pnp.plugins.pull.io import FSSize, FSWatcher


FileSystemWatcher = FSWatcher
Size = FSSize
