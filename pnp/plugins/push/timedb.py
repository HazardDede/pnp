"""push.timedb for backwards compatibility reasons."""

from pnp.plugins.push.storage import Influx

InfluxPush = Influx

__all__ = [
    'InfluxPush'
]
