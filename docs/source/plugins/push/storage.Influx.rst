storage.Influx
^^^^^^^^^^^^^^^^^

=================================== ====== ============ ========
plugin                              type   extra        version
=================================== ====== ============ ========
pnp.plugins.push.storage.Influx     push   none         < 0.10.0
=================================== ====== ============ ========

**Description**

Pushes the given ``payload`` to an influx database using the ``line protocol``.
You have to specify ``host``, ``port``, ``user``, ``password`` and the ``database``.

The ``protocol`` is basically a string that will be augmented at push-time with data from the payload.
E.g. ``{payload.metric},room={payload.location} value={payload.value}`` assumes that payload contains ``metric``, ``location``
and ``value``.


.. seealso::

   `Influx line protocol <https://docs.influxdata.com/influxdb/v1.5/write_protocols/line_protocol_tutorial/>`_


**Arguments**

+-----------+------+------+---------+-----+-------------------------------------------------------+
| name      | type | opt. | default | env | description                                           |
+===========+======+======+=========+=====+=======================================================+
| host      | str  | no   | n/a     | no  | The host where influx service is running.             |
+-----------+------+------+---------+-----+-------------------------------------------------------+
| port      | int  | no   | n/a     | no  | The port where the influx service is listening on.    |
+-----------+------+------+---------+-----+-------------------------------------------------------+
| user      | str  | no   | n/a     | no  | Username to use for authentication.                   |
+-----------+------+------+---------+-----+-------------------------------------------------------+
| password  | str  | no   | n/a     | no  | Related password.                                     |
+-----------+------+------+---------+-----+-------------------------------------------------------+
| database  | str  | no   | n/a     | no  | The database to store the measurement.                |
+-----------+------+------+---------+-----+-------------------------------------------------------+
| protocol  | str  | no   | n/a     | no  | Line protocol template (augmented with payload-data). |
+-----------+------+------+---------+-----+-------------------------------------------------------+

**Result**

For the ability to chain multiple pushes together the payload is simply returned as is.

**Example**

.. literalinclude:: ../code-samples/plugins/push/storage.Influx/example.yaml
   :language: YAML
