from . import PushBase
from ...utils import auto_str_ignore


@auto_str_ignore(['password'])
class InfluxPush(PushBase):
    """
    Pushes the given `payload` to an influx database using the line `protocol`.
    You have to specify `host`, `port`, `user`, `password` and the `database`.

    The `protocol` is basically a string that will be augmented at push-time with data from the payload.
    E.g. {payload.metric},room={payload.location} value={payload.value} assumes that payload contains metric, location
    and value.

    Args:
        host (str): The host where the influxdb is running.
        port (int): The port where the influxdb service is listening on.
        user (str): Username to use for authentication.
        password (str): Related password.
        database (str): The database to write to.
        protocol (str): Line protocol template (augmented with payload-data).
            See https://docs.influxdata.com/influxdb/v1.5/write_protocols/line_protocol_tutorial/.

    Returns:
        For the ability to chain multiple pushes together the payload is simply returned as is.
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
        envelope, real_payload = self.envelope_payload(payload)

        points = [self.protocol.format(payload=real_payload)]
        self.logger.debug("[{name}] Writing '{points}' to influxdb".format(name=self.name, points=str(points)))

        from influxdb import InfluxDBClient
        client = InfluxDBClient(self.host, self.port, self.user, self.password, self.database)
        client.write(points, {'db': self.database}, 204, 'line')

        return payload  # Payload as is. With envelope (if any)
