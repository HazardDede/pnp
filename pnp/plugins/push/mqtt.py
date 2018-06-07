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
        topic (str): The topic to subscribe to.

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

    def __init__(self, host, topic, port=1883, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.topic = str(topic)
        self.port = int(port)

    def push(self, payload):
        import paho.mqtt.publish as publish
        publish.single(topic=self.topic, payload=payload, hostname=self.host, port=self.port)
        self.logger.debug("[{self.name}] Published message on '{self.topic}' @ {self.host}:{self.port}. "
                          "Payload='{payload}'".format(**locals()))
        return payload
