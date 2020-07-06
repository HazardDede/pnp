mqtt.Subscribe
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.mqtt.Subscribe  pull   none         < 0.10.0
================================ ====== ============ ========

**Description**

Pulls messages from the specified topic from the given mosquitto mqtt broker (identified by host and port).


**Arguments**

+-------+------+------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| name  | type | opt. | default | description                                                                                                                                              |
+=======+======+======+=========+==========================================================================================================================================================+
| host  | str  | no   | n/a     | Host where the mosquitto broker is running.                                                                                                              |
+-------+------+------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| port  | int  | no   | n/a     | Port where the mosquitto broker is listening.                                                                                                            |
+-------+------+------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| topic | str  | no   | n/a     | Topic to listen for new messages. You can listen to multiple topics by using the #-wildcard (e.g. ``test/#`` will listen to all topics underneath test). |
+-------+------+------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------+


**Result**

The emitted message will look like this:


.. code-block:: python

   {
     "topic": "test/device/device1",
     "levels": ["test", "device", "device1"]
     "payload": "The actual event message"
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/mqtt.Subscribe/example.yaml
   :language: YAML