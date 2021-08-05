"""Push: mqtt.Publish."""
from typing import Optional, Any, cast

from pnp.plugins.push import SyncPush
from pnp.plugins.push.envelope import Envelope
from pnp.typing import Payload, Envelope as EnvelopeType
from pnp.utils import try_parse_bool
from .base import MQTTBase


class Publish(MQTTBase, SyncPush):
    """
    This push will push the given `payload` to a mqtt broker (in this case mosquitto).
    The broker is specified by `host` and `port`. In addition a topic needs to be specified
    were the payload is pushed to (e.g. home/living/thermostat).

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#mqtt-publish
    """
    __REPR_FIELDS__ = ['multi', 'retain', 'topic']

    def __init__(
            self, topic: Optional[str] = None, retain: bool = False,
            multi: bool = False, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.topic = self._parse_topic(topic)
        self.retain = self._parse_retain(retain)
        self.multi = bool(multi)

    @staticmethod
    def _parse_retain(val: Any) -> bool:
        return cast(bool, try_parse_bool(val, default=False))

    @staticmethod
    def _parse_topic(val: Any) -> Optional[str]:
        return str(val) if val is not None else None

    @staticmethod
    def _topic_concat(topic1: str, topic2: str) -> str:
        if str(topic1).endswith('/'):
            return topic1 + topic2
        return topic1 + '/' + topic2

    @Envelope.unwrap
    @Envelope.parse('topic')
    @Envelope.parse('retain')
    @Envelope.parse('qos')
    def _push_unwrap(
            self, topic: str, retain: bool, qos: int, envelope: EnvelopeType, payload: Payload
    ) -> Payload:  # pylint: disable=arguments-differ
        if topic is None:
            raise ValueError("Topic was not defined either by the __init__ nor by the envelope")

        if not self.multi:
            self._publish(payload, topic, retain, qos)
        else:
            if not isinstance(payload, dict):
                raise TypeError("In multi mode the payload is required to be a dictionary")
            for k, v in payload.items():
                key_topic = self._topic_concat(topic, k)
                try:
                    self._publish(v, key_topic, retain, qos)
                except:  # pylint: disable=bare-except
                    self.logger.exception(
                        "Publishing failed for message on '%s' @ "
                        "%s:%s with qos=%s. Payload='%s'",
                        key_topic, self.host, self.port, qos, v
                    )

        return {'data': payload, **envelope} if envelope else payload

    def _push(self, payload: Payload) -> Payload:
        return self._push_unwrap(payload)  # pylint: disable=no-value-for-parameter
