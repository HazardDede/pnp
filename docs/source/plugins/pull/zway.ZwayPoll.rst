zway.ZwayPoll
^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.zway.ZwayPoll   poll   none         < 0.10.0
================================ ====== ============ ========

**Description**

Pulls the specified json content from the zway rest api. The content is specified by the url, e.g.
``http://<host>:8083/ZWaveAPI/Run/devices`` will pull all devices and serve the result as a json.

Specify the polling interval by setting the argument ``interval``. User / password combination is required when
your api is protected against guest access (by default it is).

Use multiple pushes and the related selectors to extract the required content like temperature readings (see
the examples section for guidance).

**Arguments**

+----------+------+------+---------+-------------------------------+
| name     | type | opt. | default | description                   |
+==========+======+======+=========+===============================+
| url      | str  | no   | n/a     | The url to poll periodically. |
+----------+------+------+---------+-------------------------------+
| user     | str  | no   | n/a     | Authentication user name.     |
+----------+------+------+---------+-------------------------------+
| password | str  | no   | n/a     | Authentication password.      |
+----------+------+------+---------+-------------------------------+

.. NOTE::

   Below are some common selector examples to fetch various metrics from various devices

   **Fibaro Motion Sensor**

   * Temperature
     ``payload[deviceid].instances[0].commandClasses[49].data[1].val.value``
   * Luminescence
     ``payload[deviceid].instances[0].commandClasses[49].data[3].val.value``

   **Fibaro Wallplug**

   * Meter
     ``payload[deviceid].instances[0].commandClasses[50].data[0].val.value``

   **Thermostat (Danfoss / other should work as well)**

   * Setpoint
     ``payload[deviceid].instances[0].commandClasses[67].data[1].val.value``

   **Battery operated devices**

   * Battery level
     ``payload[deviceid].instances[0].commandClasses[128].data.last.value``

**Result**

Emits the content of the fetched url as it is.

**Example**

.. literalinclude:: ../code-samples/plugins/pull/zway.ZwayPoll/example.yaml
   :language: YAML