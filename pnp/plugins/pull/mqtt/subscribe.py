"""MQTT related plugins."""
from typing import Any, Optional

import paho.mqtt.client as paho

from pnp.plugins.pull import SyncPull


class Subscribe(SyncPull):
    """
    Pulls messages from the specified topic from the given mosquitto mqtt
    broker (identified by host and port).


    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#mqtt-subscribe
    """
    __REPR_FIELDS__ = ['host', 'port', 'topic', 'user']

    def __init__(
            self, host: str, topic: str, port: int = 1883, user: Optional[str] = None,
            password: Optional[str] = None, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.host = str(host)
        self.topic = str(topic)
        self.port = int(port)
        self.user = user and str(user)
        self.password = password and str(password)
        self._client = None

    def _on_connect(self, client: paho.Client, userdata: Any, flags: Any, rc: int) -> None:
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        _, _ = userdata, flags

        if rc == 0:
            client.subscribe(self.topic)
            self.logger.info("Connected with result code '%s' "
                             "to %s @ %s:%s", rc, self.topic, self.host, self.port)
        else:
            self.logger.error("Bad connection with result code '%s' "
                              "to %s @ %s:%s", rc, self.topic, self.host, self.port)

    def _on_disconnect(self, client: Any, userdata: Any, rc: int) -> None:
        _, _ = client, userdata
        if rc != 0:
            self.logger.warning("Unexpected mqtt disconnect with result code '%s'. "
                                "Will automatically reconnect.", rc)

    def _on_message(self, client: Any, obj: Any, msg: paho.MQTTMessage) -> None:
        _, _ = client, obj
        self.logger.debug("Got message from broker on topic '%s'. "
                          "Payload='%s'", self.topic, msg.payload)

        # This one is an envelope with data
        self.notify(dict(
            topic=str(msg.topic),
            levels=msg.topic.split('/'),
            payload=msg.payload.decode('utf-8')
        ))

    def _stop(self) -> None:
        super()._stop()
        if self._client:
            self._client.disconnect()

    def _pull(self) -> None:
        self._client = paho.Client()
        assert self._client
        if self.user:
            self._client.username_pw_set(self.user, self.password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        self._client.connect(self.host, self.port, 60)
        self._client.loop_forever(retry_first_connection=True)
