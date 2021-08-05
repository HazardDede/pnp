"""MQTT related push plugins."""

from .discovery import Discovery
from .publish import Publish

MQTTPush = Publish

__all__ = [
    'Discovery',
    'MQTTPush',  # Here for compatibility reasons
    'Publish'
]
