net.PortProbe
^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.net.PortProbe   poll   none         0.19.0
================================ ====== ============ ========

**Description**

Periodically establishes socket connection to check if anybody is listening on a given server on a specific port.

**Arguments**

+---------+-------+------+-----------+---------------------------------------------+
| name    | type  | opt. | default   | description                                 |
+=========+=======+======+===========+=============================================+
| port    | int   | no   | n/a       | The port to probe if a service is listening |
+---------+-------+------+-----------+---------------------------------------------+
| server  | str   | yes  | localhost | Server name or ip address                   |
+---------+-------+------+-----------+---------------------------------------------+
| timeout | float | yes  | 1.0       | Timeout for remote operations               |
+---------+-------+------+-----------+---------------------------------------------+


**Result**

Emits a dictionary that contains an entry for every sensor of the plant sensor device:


.. code-block:: python

   {
     "server": "www.google.de",
     "port": 80,
     "reachable": True
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/net.PortProbe/example.yaml
   :language: YAML