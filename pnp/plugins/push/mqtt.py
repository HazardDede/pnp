"""MQTT related push plugins."""

import json
from abc import abstractmethod

from dictmentor import DictMentor, ext

from . import PushBase
from ...utils import try_parse_bool, try_parse_int, auto_str_ignore
from ...validator import Validator


@auto_str_ignore(['password'])
class _MQTTBase(PushBase):
    __prefix__ = 'mqtt'

    def __init__(self, host, port=1883, user=None, password=None, qos=0, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.port = int(port)
        self.user = user and str(user)
        self.password = password and str(password)
        self.qos = self._parse_qos(qos)

    def _parse_qos(self, val):
        pval = try_parse_int(val)
        if pval is None:
            self.logger.warning("QOS level of '%s' is not int parsable. Defaulting to 0", val)
            return 0
        if pval < 0:
            self.logger.warning("QOS level of '%s' is invalid. Defaulting to 0", val)
            return 0
        if pval > 2:
            self.logger.warning("QOS level of '%s' is invalid. Defaulting to 2", val)
            return 2
        return pval

    def _publish(self, real_payload, topic, retain=False, qos=None):
        if isinstance(real_payload, (dict, list, tuple)):
            real_payload = json.dumps(real_payload)

        auth = None
        if self.user:
            auth = dict(username=self.user, password=self.password)

        if qos is None:
            qos = self.qos

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
        self.logger.debug(
            "[%s] Published message on '%s' @ %s:%s with qos=%s. Payload='%s'",
            self.name, topic, self.host, self.port, qos, real_payload
        )

    @abstractmethod
    def push(self, payload):
        raise NotImplementedError()


@auto_str_ignore(['configured'])
class Discovery(_MQTTBase):
    """
    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/mqtt.Discovery/index.md
    """
    SUPPORTED_COMPONENTS = ['alarm_control_panel', 'binary_sensor', 'camera', 'cover', 'fan',
                            'climate', 'light', 'lock', 'sensor', 'switch']

    def __init__(self, discovery_prefix, component, config, object_id=None, node_id=None, **kwargs):
        super().__init__(**kwargs)
        self.discovery_prefix = str(discovery_prefix)
        Validator.is_instance(str, component=component)
        Validator.one_of(self.SUPPORTED_COMPONENTS, component=component)
        self.component = component
        self.object_id = self._parse_object_id(object_id)
        Validator.is_instance(dict, config=config)
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
        return base_topic, config_topic, state_topic

    def _configure(self, object_id, node_id):
        configure_key = str(object_id) + str(node_id)
        if configure_key not in self.configured:
            base_topic, config_topic, state_topic = self._topics(object_id, node_id)
            mentor = DictMentor(
                ext.Variables(
                    fail_on_unset=True,
                    discovery_prefix=self.discovery_prefix,
                    component=self.component,
                    object_id=object_id,
                    node_id=node_id,
                    base_topic=base_topic,
                    config_topic=config_topic,
                    state_topic=state_topic
                )
            )
            config_augmented = mentor.augment(self.config)
            self._publish(config_augmented, config_topic, retain=True)
            self.configured[configure_key] = True

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)
        object_id = self._parse_envelope_value('object_id', envelope)
        node_id = self._parse_envelope_value('node_id', envelope)

        if object_id is None:
            raise ValueError("object_id was not defined either by the __init__ nor by the envelope")

        self._configure(object_id, node_id)
        _, _, state_topic = self._topics(object_id, node_id)
        self._publish(real_payload, state_topic, retain=True)

        return payload


class Publish(_MQTTBase):
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

    def _push_single(self, payload):
        envelope, real_payload = self.envelope_payload(payload)
        topic = self._parse_envelope_value('topic', envelope)  # Override topic via envelope
        retain = self._parse_envelope_value('retain', envelope)  # Override retain via envelope
        qos = self._parse_envelope_value('qos', envelope)  # Override qos via envelope

        if topic is None:
            raise ValueError("Topic was not defined either by the __init__ nor by the envelope")

        if not self.multi:
            self._publish(real_payload, topic, retain, qos)
        else:
            if not isinstance(real_payload, dict):
                raise TypeError("In multi mode the payload is required to be a dictionary")
            for k, v in real_payload.items():
                key_topic = self._topic_concat(topic, k)
                try:
                    self._publish(v, key_topic, retain, qos)
                except:  # pylint: disable=bare-except
                    import traceback
                    self.logger.error(
                        "[%s] Publishing failed for message on '%s' @ "
                        "%s:%s with qos=%s. Payload='%s'\n%s",
                        self.name, key_topic, self.host, self.port, qos, v, traceback.format_exc()
                    )

    def push(self, payload):
        self._push_single(payload)
        return payload  # Payload as is. With envelope (if any).


MQTTPush = Publish
