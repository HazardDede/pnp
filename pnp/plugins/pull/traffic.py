"""Contains traffic (trains, cars, flights, ...) related pulls."""

from datetime import datetime

from glom import glom, Coalesce
from schiene import Schiene

from pnp.plugins.pull import Polling


def _not(value):
    return not value


class DeutscheBahn(Polling):
    """Pulls the next trains that start from the origin destined for the given destination."""

    # Basically to easily adapt when the schiene package changes
    SPEC = {
        'departure': ('departure', str),
        'arrival': ('arrival', str),
        'travel_time': ('time', str),
        'products': 'products',
        'transfers': 'transfers',
        'canceled': 'canceled',
        'delayed': ('ontime', _not),
        'delay_departure': Coalesce('delay.delay_departure', default=0),
        'delay_arrival': Coalesce('delay.delay_arrival', default=0),
    }

    def __init__(self, origin, destination, only_direct=False, **kwargs):
        super().__init__(**kwargs)
        self.origin = str(origin)
        self.destination = str(destination)
        self.only_direct = bool(only_direct)

    def poll(self):
        api = Schiene()
        connections = api.connections(
            self.origin,
            self.destination,
            only_direct=self.only_direct,
            dt=datetime.now()
        )
        return [glom(conn, self.SPEC) for conn in connections]
