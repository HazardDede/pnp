mqtt.Discovery
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.push.mqtt.Discovery  push   none         0.13.0
================================ ====== ============ ========

**Description**

Pushes an entity to home assistant by publishing it to an mqtt broker.
The entity will be enabled to be auto discovered by home assistant.

Please see the home assistant `docs about mqtt auto discovery <https://www.home-assistant.io/docs/mqtt/discovery/>`_.

The mqtt topic is structured like this:

``<discovery_prefix>/<component>/[<node_id>/]<object_id>/[config|state]``

You may also publish ``attributes`` besides your state. ``attributes`` can be passed by the envelope
via runtime. Please see the examples section for further reference.

**Arguments**

+------------------+------+------+---------+-----+---------------------------------------------------------------------------------------------------------+
| name             | type | opt. | default | env | description                                                                                             |
+==================+======+======+=========+=====+=========================================================================================================+
| discovery_prefix | str  | no   | n/a     | no  | The prefix for the topic.                                                                               |
+------------------+------+------+---------+-----+---------------------------------------------------------------------------------------------------------+
| component        | str  | no   | n/a     | no  | The component / type of the entity, e.g. ``sensor``, ``light``, ...                                     |
+------------------+------+------+---------+-----+---------------------------------------------------------------------------------------------------------+
| config           | Dict | no   | n/a     | no  | A dictionary of configuration items to configure the entity (e.g. ``icon`` -> ``mdi:soccer``)           |
+------------------+------+------+---------+-----+---------------------------------------------------------------------------------------------------------+
| object_id        | str  | yes  | None    | yes | The ID of the device. This is only to allow for separate topics for each device and is not used for the |
|                  |      |      |         |     | entity_id.                                                                                              |
+------------------+------+------+---------+-----+---------------------------------------------------------------------------------------------------------+
| node_id          | str  | yes  | None    | yes | A non-interpreted structuring entity to structure the MQTT topic.                                       |
+------------------+------+------+---------+-----+---------------------------------------------------------------------------------------------------------+

.. NOTE::

   Inside the ``config`` section you can reference some variables to make the configuration easier.
   The following variables can be referenced via the ``dictmentor`` syntax ``"{{var::<variable>}}"``:

   * discovery_prefix
   * component
   * object_id
   * node_id
   * base_topic
   * config_topic
   * state_topic
   * json_attributes_topic

   Please see the examples section on how to use that.


**Result**

Returns the payload as-is for better chaining (this plugin can't add any useful information).

**Example**

.. literalinclude:: ../code-samples/plugins/push/mqtt.Discovery/example.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/push/mqtt.Discovery/example2.yaml
   :language: YAML
