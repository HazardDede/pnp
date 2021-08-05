"""Push: mqtt.Discovery."""
from typing import Any, Dict, Optional, Tuple

from dictmentor import DictMentor, ext

from pnp import validator
from pnp.plugins.push import SyncPush
from pnp.plugins.push.envelope import Envelope
from pnp.typing import Payload
from .base import MQTTBase

AutoDiscoveryConfig = Dict[str, Any]


class Discovery(MQTTBase, SyncPush):
    """
    Pushes an entity to home assistant by publishing it to an mqtt broker.
    The entity will be enabled to be auto discovered by home assistant.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#mqtt-discovery
    """
    __REPR_FIELDS__ = ['component', 'discovery_prefix', 'node_id', 'object_id']

    SUPPORTED_COMPONENTS = ['alarm_control_panel', 'binary_sensor', 'camera', 'cover', 'fan',
                            'climate', 'light', 'lock', 'sensor', 'switch']

    CONST_STATE_TOPIC = 'state_topic'
    CONST_JSON_ATTRIBUTES_TOPIC = 'json_attributes_topic'

    def __init__(
            self, discovery_prefix: str, component: str, config: AutoDiscoveryConfig,
            object_id: Optional[str] = None, node_id: Optional[str] = None, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.discovery_prefix = str(discovery_prefix)
        validator.one_of(self.SUPPORTED_COMPONENTS, component=str(component))
        self.component = str(component)
        self.object_id = self._parse_object_id(object_id)
        validator.is_instance(dict, config=config)
        self._config = config
        self.node_id = self._parse_node_id(node_id)
        self.configured: Dict[str, bool] = {}

    @property
    def config(self) -> AutoDiscoveryConfig:
        """Return the mqtt discovery configuration."""
        import copy
        return copy.copy(self._config)

    @staticmethod
    def _parse_object_id(val: Any) -> str:
        return str(val)

    @staticmethod
    def _parse_node_id(val: Any) -> Optional[str]:
        return val and str(val)

    def _topics(self, object_id: str, node_id: Optional[str]) -> Tuple[str, str, str, str]:
        node_id = "{node_id}/".format(node_id=node_id) if node_id else ""
        base_topic = "{prefix}/{component}/{node_id}{object_id}".format(
            prefix=self.discovery_prefix,
            component=self.component,
            node_id=node_id,
            object_id=object_id
        )
        state_topic = base_topic + "/state"
        config_topic = base_topic + "/config"
        attr_topic = base_topic + "/attributes"
        return base_topic, config_topic, state_topic, attr_topic

    def _configure(self, object_id: str, node_id: Optional[str]) -> None:
        configure_key = str(object_id) + str(node_id)
        if configure_key not in self.configured:
            base_topic, config_topic, state_topic, attr_topic = self._topics(object_id, node_id)
            mentor = DictMentor(
                ext.Variables(
                    fail_on_unset=True,
                    discovery_prefix=self.discovery_prefix,
                    component=self.component,
                    object_id=object_id,
                    node_id=node_id,
                    base_topic=base_topic,
                    config_topic=config_topic,
                    **{
                        self.CONST_STATE_TOPIC: state_topic,
                        self.CONST_JSON_ATTRIBUTES_TOPIC: attr_topic
                    }
                )
            )
            config_augmented = mentor.augment(self.config)
            if self.CONST_STATE_TOPIC in config_augmented:
                self.logger.warning(
                    "%s is part of your config, but will be ignored",
                    self.CONST_STATE_TOPIC
                )
            if self.CONST_JSON_ATTRIBUTES_TOPIC in config_augmented:
                self.logger.warning(
                    "%s is part of your config, but will be ignored",
                    self.CONST_JSON_ATTRIBUTES_TOPIC
                )

            config_augmented[self.CONST_STATE_TOPIC] = state_topic
            config_augmented[self.CONST_JSON_ATTRIBUTES_TOPIC] = attr_topic

            self._publish(config_augmented, config_topic, retain=True)
            self.configured[configure_key] = True

    @Envelope.unwrap
    @Envelope.parse('object_id')
    @Envelope.parse('node_id')
    @Envelope.parse('attributes')
    @Envelope.drop
    def _push_unwrap(
            self, object_id: str, node_id: Optional[str], attributes: AutoDiscoveryConfig,
            payload: Payload
    ) -> Payload:
        if object_id is None:
            raise ValueError("object_id was not defined either by the __init__ nor by the envelope")

        self._configure(object_id, node_id)
        _, _, state_topic, attribute_topic = self._topics(object_id, node_id)
        self._publish(payload, state_topic, retain=True)

        if attributes and isinstance(attributes, dict):
            self._publish(attributes, attribute_topic, retain=True)

        return payload

    def _push(self, payload: Payload) -> Payload:
        return self._push_unwrap(payload)  # pylint: disable=no-value-for-parameter
