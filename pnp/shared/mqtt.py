"""MQTT related utility classes."""

import json
import logging

from ..utils import auto_str_ignore, try_parse_int

_LOGGER = logging.getLogger(__name__)


@auto_str_ignore(['password'])
class MQTTBase:
    """MQTT base class for publising message to a mqtt broker."""

    def __init__(self, host, port=1883, user=None, password=None, qos=0, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.port = int(port)
        self.user = user and str(user)
        self.password = password and str(password)
        self.qos = self._parse_qos(qos)

    @staticmethod
    def _parse_qos(val):
        pval = try_parse_int(val)
        if pval is None:
            _LOGGER.warning("QOS level of '%s' is not int parsable. Defaulting to 0", val)
            return 0
        if pval < 0:
            _LOGGER.warning("QOS level of '%s' is invalid. Defaulting to 0", val)
            return 0
        if pval > 2:
            _LOGGER.warning("QOS level of '%s' is invalid. Defaulting to 2", val)
            return 2
        return pval

    def _publish(self, payload, topic, retain=False, qos=None):
        if isinstance(payload, (dict, list, tuple)):
            payload = json.dumps(payload)

        auth = None
        if self.user:
            auth = dict(username=self.user, password=self.password)

        if qos is None:
            qos = self.qos

        import paho.mqtt.publish as publish
        publish.single(
            topic=topic,
            payload=payload,
            hostname=self.host,
            port=self.port,
            retain=retain,
            auth=auth,
            qos=qos
        )
        _LOGGER.debug(
            "Published message on '%s' @ %s:%s with qos=%s. Payload='%s'",
            topic, self.host, self.port, qos, payload
        )
