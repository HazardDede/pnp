"""pull.ftp for backwards compatibility reasons."""

# pylint: disable=no-name-in-module
from pnp.plugins.pull.net import FTPServer

Server = FTPServer

__all__ = [
    'Server'
]
