sensor.DHT
^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.sensor.DHT      poll   dht          < 0.10.0
================================ ====== ============ ========

**Description**

Periodically polls a **dht11** or **dht22** (aka **am2302**) for temperature and humidity readings.
Polling interval is controlled by ``interval``.

**Arguments**

+-----------------+-------+------+---------+---------------------------------------------------+
| name            | type  | opt. | default | description                                       |
+=================+=======+======+=========+===================================================+
| device          | str   | yes  | dht22   | The device to poll (one of dht22, dht11, am2302). |
+-----------------+-------+------+---------+---------------------------------------------------+
| data_gpio       | int   | yes  | 17      | The data gpio port where the device operates on.  |
+-----------------+-------+------+---------+---------------------------------------------------+
| humidity_offset | float | yes  | 0.0     | Positive/Negative offset for humidity.            |
+-----------------+-------+------+---------+---------------------------------------------------+
| temp_offset     | float | yes  | 0.0     | Positive/Negative offset for temperature.         |
+-----------------+-------+------+---------+---------------------------------------------------+

**Result**

.. code-block:: python

   {
     "humidity": 65.4  # in %
     "temperature": 23.7  # in celsius
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/sensor.DHT/example.yaml
   :language: YAML