"""push.timedb for backwards compatibility reasons."""

from pnp.plugins.push.storage import Influx  # type: ignore

InfluxPush = Influx

__all__ = [
    'InfluxPush'
]
