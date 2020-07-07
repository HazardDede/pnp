traffic.DeutscheBahn
^^^^^^^^^^^^^^^^^^^^

====================================== ====== ============ ========
plugin                                 type   extra        version
====================================== ====== ============ ========
pnp.plugins.pull.traffic.DeutscheBahn  poll   none         0.19.0
====================================== ====== ============ ========

**Description**

Polls the Deutsche Bahn website using the ``schiene`` package to find the next trains scheduled
for a given destination from a specific origin station.

**Arguments**

+-------------+------+------+---------+-----------------------------------------------------------------+
| name        | type | opt. | default | description                                                     |
+=============+======+======+=========+=================================================================+
| origin      | str  | no   | n/a     | The origin station.                                             |
+-------------+------+------+---------+-----------------------------------------------------------------+
| destination | str  | no   | n/a     | The destination station.                                        |
+-------------+------+------+---------+-----------------------------------------------------------------+
| only_direct | bool | yes  | False   | If set to True only show direct connections (without transfer). |
+-------------+------+------+---------+-----------------------------------------------------------------+

**Result**

.. code-block:: python

   [{
     "departure": "09:01",
     "arrival": "15:09",
     "travel_time": "6:05",
     "products": ["ICE"],
     "transfers": 1,
     "canceled": false,
     "delayed": true,
     "delay_departure": 3,
     "delay_arrival": 0
   }, {
     "departure": "09:28",
     "arrival": "15:39",
     "travel_time": "6:11",
     "products": ["ICE"],
     "transfers": 0,
     "canceled": false,
     "delayed": false,
     "delay_departure": 0,
     "delay_arrival": 0
   }, {
     "departure": "09:36",
     "arrival": "16:02",
     "travel_time": "6:26",
     "products": ["ICE"],
     "transfers": 1,
     "canceled": false,
     "delayed": false,
     "delay_departure": 0,
     "delay_arrival": 0
   }]

**Example**

.. literalinclude:: ../code-samples/plugins/pull/traffic.DeutscheBahn/example.yaml
   :language: YAML