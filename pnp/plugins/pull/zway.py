"""Z-Way related plugins for backwards compatibility."""

# pylint: disable=no-name-in-module
from pnp.plugins.pull.http import ZwayFetch


ZwayPoll = ZwayFetch
