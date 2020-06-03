"""MQTT related utility classes."""

import json
import logging
from typing import Optional, Any

from pnp.typing import Payload
from pnp.utils import auto_str_ignore, try_parse_int

_LOGGER = logging.getLogger(__name__)


@auto_str_ignore(['password'])
class MQTTBase:
    """MQTT base class for publishing message to a mqtt broker."""

    def __init__(
        self, host: str, port: int = 1883, user: Optional[str] = None,
        password: Optional[str] = None, qos: int = 0, **kwargs: Any
    ):
        super().__init__(**kwargs)  # type: ignore
        self.host = str(host)
        self.port = int(port)
        self.user = user and str(user)
        self.password = password and str(password)
        self.qos = self._parse_qos(qos)

    @staticmethod
    def _parse_qos(val: int) -> int:
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

    def _publish(
        self, payload: Payload, topic: str, retain: bool = False, qos: Optional[int] = None
    ) -> None:
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
