from . import PushBase
from ...utils import try_parse_bool, try_parse_int


class Publish(PushBase):
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

    def __init__(self, host, topic=None, port=1883, retain=False, user=None, password=None, qos=0,
                 multi=False, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.topic = self._parse_topic(topic)
        self.port = int(port)
        self.retain = self._parse_retain(retain)
        self.user = user and str(user)
        self.password = password and str(password)
        self.qos = self._parse_qos(qos)
        self.multi = bool(multi)

    def _parse_retain(self, val):
        return try_parse_bool(val, default=False)

    def _parse_topic(self, val):
        return str(val) if val is not None else None

    def _parse_qos(self, val):
        pval = try_parse_int(val)
        if pval is None:
            self.logger.warning("QOS level of '{val}' is not int parsable. Defaulting to 0".format(**locals()))
            return 0
        if pval < 0:
            self.logger.warning("QOS level of '{val}' is invalid. Defaulting to 0".format(**locals()))
            return 0
        if pval > 2:
            self.logger.warning("QOS level of '{val}' is invalid. Defaulting to 2".format(**locals()))
            return 2
        return pval

    def _publish(self, auth, qos, real_payload, retain, topic):
        import paho.mqtt.publish as publish

        publish.single(
            topic=topic,
            payload=real_payload,
            hostname=self.host,
            port=self.port,
            retain=retain,
            auth=auth,
            qos=qos
        )
        self.logger.debug("[{self.name}] Published message on '{topic}' @ {self.host}:{self.port} with qos={qos}. "
                          "Payload='{real_payload}'".format(**locals()))

    @staticmethod
    def _topic_concat(t1, t2):
        if str(t1).endswith('/'):
            return t1 + t2
        return t1 + '/' + t2

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)
        topic = self._parse_envelope_value('topic', envelope)  # Override topic via envelope
        retain = self._parse_envelope_value('retain', envelope)  # Override retain via envelope
        qos = self._parse_envelope_value('qos', envelope)  # Override qos via envelope

        if topic is None:
            raise ValueError("Topic was not defined either by the __init__ nor by the envelope")

        auth = None
        if self.user:
            auth = dict(username=self.user, password=self.password)
        if not self.multi:
            self._publish(auth, qos, real_payload, retain, topic)
        else:
            if not isinstance(real_payload, dict):
                raise TypeError("In multi mode the payload is required to be a dictionary")
            for k, v in real_payload.items():
                key_topic = self._topic_concat(topic, k)
                try:
                    self._publish(auth, qos, v, retain, key_topic)
                except:
                    import traceback
                    ex = traceback.format_exc()
                    self.logger.error("[{self.name}] Publishing failed for message on '{key_topic}' @ "
                                      "{self.host}:{self.port} with qos={qos}. Payload='{v}'\n{ex}".format(**locals()))

        return payload  # Payload as is. With envelope (if any).


MQTTPush = Publish
