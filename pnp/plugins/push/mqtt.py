"""MQTT related push plugins."""

from dictmentor import DictMentor, ext

from pnp import validator
from pnp.plugins.push import PushBase, enveloped, parse_envelope, drop_envelope
from pnp.shared.mqtt import MQTTBase
from pnp.utils import try_parse_bool, auto_str_ignore


@auto_str_ignore(['configured'])
class Discovery(MQTTBase, PushBase):
    """
    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/mqtt.Discovery/index.md
    """
    SUPPORTED_COMPONENTS = ['alarm_control_panel', 'binary_sensor', 'camera', 'cover', 'fan',
                            'climate', 'light', 'lock', 'sensor', 'switch']

    def __init__(self, discovery_prefix, component, config, object_id=None, node_id=None, **kwargs):
        super().__init__(**kwargs)
        self.discovery_prefix = str(discovery_prefix)
        validator.is_instance(str, component=component)
        validator.one_of(self.SUPPORTED_COMPONENTS, component=component)
        self.component = component
        self.object_id = self._parse_object_id(object_id)
        validator.is_instance(dict, config=config)
        self._config = config
        self.node_id = self._parse_node_id(node_id)
        self.configured = {}

    @property
    def config(self):
        """Return the mqtt discovery configuration."""
        import copy
        return copy.copy(self._config)

    @staticmethod
    def _parse_object_id(val):
        return str(val)

    @staticmethod
    def _parse_node_id(val):
        return val and str(val)

    def _topics(self, object_id, node_id):  # pylint: disable=unused-argument
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

    def _configure(self, object_id, node_id):
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
                    state_topic=state_topic,
                    json_attributes_topic=attr_topic
                )
            )
            config_augmented = mentor.augment(self.config)
            self._publish(config_augmented, config_topic, retain=True)
            self.configured[configure_key] = True

    @enveloped
    @parse_envelope('object_id')
    @parse_envelope('node_id')
    @parse_envelope('attributes')
    @drop_envelope
    def push(self, object_id, node_id, attributes, payload):  # pylint: disable=arguments-differ
        if object_id is None:
            raise ValueError("object_id was not defined either by the __init__ nor by the envelope")

        self._configure(object_id, node_id)
        _, _, state_topic, attribute_topic = self._topics(object_id, node_id)
        self._publish(payload, state_topic, retain=True)

        if attributes and isinstance(attributes, dict):
            self._publish(attributes, attribute_topic, retain=True)

        return payload


class Publish(MQTTBase, PushBase):
    """
    This push will push the given `payload` to a mqtt broker (in this case mosquitto).
    The broker is specified by `host` and `port`. In addition a topic needs to be specified
    were the payload is pushed to (e.g. home/living/thermostat).

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/mqtt.Publish/index.md
    """

    def __init__(self, topic=None, retain=False, multi=False, **kwargs):
        super().__init__(**kwargs)
        self.topic = self._parse_topic(topic)
        self.retain = self._parse_retain(retain)
        self.multi = bool(multi)

    @staticmethod
    def _parse_retain(val):
        return try_parse_bool(val, default=False)

    @staticmethod
    def _parse_topic(val):
        return str(val) if val is not None else None

    @staticmethod
    def _topic_concat(topic1, topic2):
        if str(topic1).endswith('/'):
            return topic1 + topic2
        return topic1 + '/' + topic2

    @enveloped
    @parse_envelope('topic')
    @parse_envelope('retain')
    @parse_envelope('qos')
    def push(self, topic, retain, qos, envelope, payload):  # pylint: disable=arguments-differ
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


MQTTPush = Publish
