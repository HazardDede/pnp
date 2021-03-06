monitor.Stats
^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.monitor.Stats   poll   none         0.12.0
================================ ====== ============ ========

**Description**

Emits every ``interval`` various metrics / statistics about the host system.
Please see the ``Result`` section for available metrics.


**Result**

Emits a dictionary that contains an entry for every sensor of the plant sensor device:


.. code-block:: python

   {
     "cpu_count": 4,
     "cpu_freq": 2700,
     "cpu_temp": 0.0,
     "cpu_use": 80.0,
     "disk_use": 75.1,
     "load_1m": 2.01171875,
     "load_5m": 1.89501953125,
     "load_15m": 1.94189453125,
     "memory_use": 67.0,
     "rpi_cpu_freq_capped": 0,
     "rpi_temp_limit_throttle": 0,
     "rpi_throttle": 0,
     "rpi_under_voltage": 0,
     "swap_use": 36.1
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/monitor.Stats/example.yaml
   :language: YAML