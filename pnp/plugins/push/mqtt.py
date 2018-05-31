import paho.mqtt.publish as publish

from . import PushBase


class MQTTPush(PushBase):
    __prefix__ = 'mqtt'

    def __init__(self, host, topic, port=1883, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.topic = str(topic)
        self.port = int(port)

    def push(self, payload):
        publish.single(topic=self.topic, payload=payload, hostname=self.host, port=self.port)
        self.logger.debug("[{self.name}] Published message on '{self.topic}' @ {self.host}:{self.port}. "
                          "Payload='{payload}'".format(**locals()))
        return payload
