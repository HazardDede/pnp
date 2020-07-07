sensor.MiFlora
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.sensor.MiFlora  poll   miflora      0.16.0
================================ ====== ============ ========

**Description**

Periodically polls a ``Xiaomi MiFlora plant sensor`` for sensor readings
(temperature, conductivity, light, ...) via btle

**Arguments**

+---------+------+------+---------+-------------------------------------------------------------+
| name    | type | opt. | default | description                                                 |
+=========+======+======+=========+=============================================================+
| mac     | str  | no   | n/a     | The device to poll identified by mac address.               |
|         |      |      |         |                                                             |
|         |      |      |         | See below for further instructions                          |
+---------+------+------+---------+-------------------------------------------------------------+
| adapter | str  | yes  | hci0    | The bluetooth adapter to use (if you have more than one).   |
|         |      |      |         |                                                             |
|         |      |      |         | Default is ``hci0`` which is your default bluetooth device. |
+---------+------+------+---------+-------------------------------------------------------------+

.. NOTE::

   Start a bluetooth scan to determine the MAC addresses of the sensor (look for Flower care or Flower mate entries)
   using this command:

   .. code-block:: shell

      $ sudo hcitool lescan
      LE Scan ...
      F8:04:33:AF:AB:A2 [TV] UE48JU6580
      C4:D3:8C:12:4C:57 Flower mate
      [...]

**Result**

Emits a dictionary that contains an entry for every sensor of the plant sensor device:


.. code-block:: python

   {
     "conductivity": 800,
     "light": 2000,
     "moisture": 42,
     "battery": 72,
     "temperature": 24.2,
     "firmaware": "3.1.9"
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/sensor.MiFlora/example.yaml
   :language: YAML