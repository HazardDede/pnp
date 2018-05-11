from . import PullBase


class MQTTPull(PullBase):
    __prefix__ = 'mqtt'

    def __init__(self, host, topic, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.topic = topic

    def on_connect(self, client, userdata, flags, rc):
        self.logger.debug("[{name}] Connected with result code '{rc}' to {topic}@{host}".format(
            name=self.name, rc=str(rc), topic=self.topic, host=self.host))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.topic)

    def on_message(self, client, obj, msg):
        self.logger.debug("[{name}] Got message from broker on topic '{topic}'. Payload='{payload}'".format(
            name=self.name, topic=msg.topic, payload=str(msg.payload)))
        self.notify(dict(
            topic=str(msg.topic),
            levels=[level for level in msg.topic.split('/')],
            payload=str(msg.payload.decode('utf-8'))
        ))

    def pull(self):
        import paho.mqtt.client as paho

        client = paho.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(self.host, 1883, 60)
        while not self.stopped:
            client.loop()