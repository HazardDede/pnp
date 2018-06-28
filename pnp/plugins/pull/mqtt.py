from . import PullBase


class MQTTPull(PullBase):
    """
    Pulls messages from the specified topic from the given mosquitto mqtt broker (identified by host and port).

    All arguments (`host`, `port` and `topic`) can be automatically injected via environment variables.
    * MQTT_HOST
    * MQTT_PORT
    * MQTT_TOPIC

    Args:
        host (str): The host where the mosquitto broker is running.
        port (int): The port where the mosquitto broker is listening (default is 1883).
        topic (str): The topic to publish to.

    Returns:
        The callback `on_payload` will offer a payload that is a dictionary of the received event.
        Example ->
        {
            'topic': 'test/device/device1',
            'levels': ['test', 'device', 'device1']
            'payload': 'The actual event message'
        }

    Example configuration:

        name: mqtt
        pull:
          plugin: pnp.plugins.pull.mqtt.MQTTPull
          args:
            host: localhost
            port: 1883
            topic: test/#
        push:
          plugin: pnp.plugins.push.simple.Echo

    """
    __prefix__ = 'mqtt'

    def __init__(self, host, topic, port=1883, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.topic = str(topic)
        self.port = int(port)

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("[{self.name}] Connected with result code '{rc}' "
                         "to {self.topic} @ {self.host}:{self.port}".format(**locals()))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.topic)

    def on_message(self, client, obj, msg):
        self.logger.debug("[{self.name}] Got message from broker on topic '{self.topic}'. "
                          "Payload='{msg.payload}'".format(**locals()))

        # This one is a envelope with data
        self.notify(dict(
            topic=str(msg.topic),
            levels=[level for level in msg.topic.split('/')],
            payload=msg.payload.decode('utf-8')
        ))

    def pull(self):
        import paho.mqtt.client as paho

        client = paho.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(self.host, self.port, 60)
        while not self.stopped:
            client.loop()
