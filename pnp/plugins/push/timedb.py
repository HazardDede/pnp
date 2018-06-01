from . import PushBase
from ...utils import auto_str_ignore


@auto_str_ignore(['password'])
class InfluxPush(PushBase):
    """
    Pushes the given `payload` to an influx database using the line `protocol`.
    You have to specify `host`, `port`, `user`, `password` and the `database`.

    The `protocol` basically is string that will be augmented at push-time with data from the payload.
    E.g. {payload.metric},room={payload.location} value={payload.value} assumes that payload contains metric, location
    and value.
    """
    __prefix__ = 'influx'

    def __init__(self, host, port, user, password, database, protocol, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.port = int(port)
        self.user = str(user)
        self.password = str(password)
        self.database = str(database)
        self.protocol = str(protocol)

    def push(self, payload):
        points = [self.protocol.format(payload=payload)]
        self.logger.debug("[{name}] Writing '{points}' to influxdb".format(name=self.name, points=str(points)))

        from influxdb import InfluxDBClient
        client = InfluxDBClient(self.host, self.port, self.user, self.password, self.database)
        client.write(points, {'db': self.database}, 204, 'line')

        return payload
