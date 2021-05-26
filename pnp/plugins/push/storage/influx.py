"""Time database related push plugins."""
from typing import Any

from influxdb import InfluxDBClient

from pnp.plugins.push import SyncPush, enveloped
from pnp.typing import Payload, Envelope


class Influx(SyncPush):
    """
    Pushes the given `payload` to an influx database using the line `protocol`.
    You have to specify `host`, `port`, `user`, `password` and the `database`.

    The `protocol` is basically a string that will be augmented at push-time with data from the
    payload. E.g. {payload.metric},room={payload.location} value={payload.value} assumes that
    payload contains metric, location and value.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#storage-influx
    """
    __REPR_FIELDS__ = ['database', 'host', 'port', 'protocol', 'user']

    def __init__(
            self, host: str, port: int, user: str, password: str, database: str, protocol: str,
            **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.host = str(host)
        self.port = int(port)
        self.user = str(user)
        self.password = str(password)
        self.database = str(database)
        self.protocol = str(protocol)

    @enveloped
    def _push_unwrap(self, envelope: Envelope, payload: Payload) -> Payload:
        points = [self.protocol.format(payload=payload)]
        self.logger.debug("Writing '%s' to influxdb", str(points))

        client = InfluxDBClient(self.host, self.port, self.user, self.password, self.database)
        client.write(points, {'db': self.database}, 204, 'line')

        return {'data': payload, **envelope} if envelope else payload

    def _push(self, payload: Payload) -> Payload:
        return self._push_unwrap(payload)  # pylint: disable=no-value-for-parameter
