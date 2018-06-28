from . import PushBase


class MQTTPush(PushBase):
    """
    This push will push the given `payload` to a mqtt broker (in this case mosquitto).
    The broker is specified by `host` and `port`. In addition a topic needs to be specified were the payload
    is pushed to (e.g. home/living/thermostat).

    The `payload` will be pushed as it is. No transformation is applied. If you need to some transformations, use the
    selector.

    Args:
        host (str): The host where the mosquitto broker is running.
        port (int): The port where the mosquitto broker is listening (default is 1883).
        topic (str): The topic to subscribe to. If set to None the envelope of the
                     payload has to contain a topic key or the push will fail (default is None). If both exists
                     the topic from the envelope will overrule the __init__ one.

    Returns:
        For chaining of pushes the payload is simply returned as is.

    Example configuration:

        name: mqtt
        pull:
          plugin: pnp.plugins.pull.simple.Count
        push:
          plugin: pnp.plugins.push.mqtt.MQTTPush
          args:
            host: localhost
            topic: home/devices/#
            port: 1883
    """
    __prefix__ = 'mqtt'

    def __init__(self, host, topic=None, port=1883, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.topic = str(topic) if topic is not None else None
        self.port = int(port)

    def push(self, payload):
        import paho.mqtt.publish as publish

        envelope, real_payload = self.envelope_payload(payload)
        topic = envelope.get('topic', self.topic)  # Override topic via envelope

        if topic is None:
            raise ValueError("Topic was not defined either by the __init__ nor by the envelope")

        publish.single(topic=topic, payload=real_payload, hostname=self.host, port=self.port)
        self.logger.debug("[{self.name}] Published message on '{topic}' @ {self.host}:{self.port}. "
                          "Payload='{payload}'".format(**locals()))
        return payload  # Payload as is. With envelope (if any).
