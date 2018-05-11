from attrdict import AttrDict
from influxdb import InfluxDBClient

from . import PushBase
from ...utils import auto_str_ignore


@auto_str_ignore(['password'])
class InfluxPush(PushBase):
    __prefix__ = 'influx'

    def __init__(self, host, port, user, password, database, protocol, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database = database
        self.protocol = protocol

    def push(self, payload):
        points = [self.protocol.format(payload=AttrDict(payload))]
        self.logger.debug("[{name}] Writing '{points}' to influxdb".format(name=self.name, points=str(points)))
        client = InfluxDBClient(self.host, self.port, self.user, self.password, self.database)
        client.write(points, {'db': self.database}, 204, 'line')
