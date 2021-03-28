"""General usage push plugins."""

from .echo import Echo
from .execute import Execute
from .nop import Nop
from .wait import Wait

__all__ = [
    'Echo',
    'Execute',
    'Nop',
    'Wait'
]
