"""pull.presence for backwards compatibility reasons."""

# pylint: disable=no-name-in-module
from pnp.plugins.pull.tracking import FritzBoxTracker
_ = FritzBoxTracker

__all__ = [
    'FritzBoxTracker'
]
