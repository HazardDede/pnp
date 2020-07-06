simple.Repeat
^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.simple.Repeat   poll   none         < 0.10.0
================================ ====== ============ ========

**Description**

Emits every ``interval`` seconds the same ``repeat``.

**Arguments**

+--------+------+------+---------+---------------------+
| name   | type | opt. | default | description         |
+========+======+======+=========+=====================+
| repeat | Any  | no   | n/a     | The object to emit. |
+--------+------+------+---------+---------------------+

**Result**

Emits the ``repeat``-object as it is.

**Example**

.. literalinclude:: ../code-samples/plugins/pull/simple.Repeat/example.yaml
   :language: YAML