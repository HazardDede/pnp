mqtt.Publish
^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.push.mqtt.Publish    push   none         < 0.10.0
================================ ====== ============ ========

**Description**

Will push the given ``payload`` to a mqtt broker e.g. ``mosquitto``.
The broker is specified by ``host`` and ``port``. In addition a ``topic`` needs to be specified were the payload
will be pushed to (e.g. ``home/living/thermostat``).

The ``payload`` will be pushed as it is. No transformation is applied. If you need to some transformations, use the
selector.

**Arguments**

+--------+------+------+---------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name   | type | opt. | default | env | description                                                                                                                                                                                                |
+========+======+======+=========+=====+============================================================================================================================================================================================================+
| host   | str  | no   | n/a     | no  | The host where the mqtt broker is running.                                                                                                                                                                 |
+--------+------+------+---------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| port   | int  | yes  | 1883    | no  | The port where the mqtt broker is listening                                                                                                                                                                |
+--------+------+------+---------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| topic  | Dict | yes  | None    | yes | The topic to subscribe to. If set to ``None`` the envelope of the payload has to contain a ``topic`` key or the push will fail. If both exists the topic from the envelope will overrule the __init__ one. |
+--------+------+------+---------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| retain | bool | yes  | False   | no  | If set to ``True`` will mark the message as retained.                                                                                                                                                      |
|        |      |      |         |     | See the mosquitto man page for further guidance: `https://mosquitto.org/man/mqtt-7.html <https://mosquitto.org/man/mqtt-7.html>`_.                                                                         |
+--------+------+------+---------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| multi  | bool | yes  | False   | no  | If set to ``True`` the payload is expected to be a dictionary. Each item of that dictionary will be send individually to the broker. The key of the item will be appended to the configured topic.         |
+--------+------+------+---------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

For chaining of pushes the payload is simply returned as it is.

**Example**

.. literalinclude:: ../code-samples/plugins/push/mqtt.Publish/example1.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/push/mqtt.Publish/example2.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/push/mqtt.Publish/example3.yaml
   :language: YAML

