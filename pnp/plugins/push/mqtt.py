import paho.mqtt.publish as publish

from . import PushBase


class MQTTPush(PushBase):
    __prefix__ = 'mqtt'

    def __init__(self, host, topic, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.topic = topic

    def push(self, payload):
        self.logger.debug("[{name}] Publishing message on '{topic}'. Payload='{payload}'".format(
            name=self.name, topic=self.topic, payload=str(payload)))
        publish.single(topic=self.topic, payload=str(payload), hostname=self.host)
