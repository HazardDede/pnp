"""MQTT related plugins."""

from pnp.plugins.pull import PullBase
from pnp.utils import auto_str_ignore


@auto_str_ignore(['_client', 'password'])
class Subscribe(PullBase):
    """
    Pulls messages from the specified topic from the given mosquitto mqtt
    broker (identified by host and port).


    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/mqtt.Subscribe/index.md
    """

    def __init__(self, host, topic, port=1883, user=None, password=None, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.topic = str(topic)
        self.port = int(port)
        self.user = user and str(user)
        self.password = password and str(password)
        self._client = None

    def _on_connect(self, client, userdata, flags, rc):  # pylint: disable=unused-argument
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        if rc == 0:
            client.subscribe(self.topic)
            self.logger.info("Connected with result code '%s' "
                             "to %s @ %s:%s", rc, self.topic, self.host, self.port)
        else:
            self.logger.error("Bad connection with result code '%s' "
                              "to %s @ %s:%s", rc, self.topic, self.host, self.port)

    def _on_disconnect(self, client, userdata, rc):  # pylint: disable=unused-argument
        if rc != 0:
            self.logger.warning("Unexpected mqtt disconnect with result code '%s'. "
                                "Will automatically reconnect.", rc)

    def _on_message(self, client, obj, msg):  # pylint: disable=unused-argument
        self.logger.debug("Got message from broker on topic '%s'. "
                          "Payload='%s'", self.topic, msg.payload)

        # This one is an envelope with data
        self.notify(dict(
            topic=str(msg.topic),
            levels=msg.topic.split('/'),
            payload=msg.payload.decode('utf-8')
        ))

    def stop(self):
        super().stop()
        if self._client:
            self._client.disconnect()

    def pull(self):
        import paho.mqtt.client as paho

        self._client = paho.Client()
        if self.user:
            self._client.username_pw_set(self.user, self.password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        self._client.connect(self.host, self.port, 60)
        self._client.loop_forever(retry_first_connection=True)


# For backwards compat
MQTTPull = Subscribe
