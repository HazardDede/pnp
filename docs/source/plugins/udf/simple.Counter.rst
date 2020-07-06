simple.Counter
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.udf.simple.Counter   udf    none         0.14.0
================================ ====== ============ ========

**Description**

Memories a counter value which is increased everytime you call the udf.

**Arguments**

+------+------+------+---------+------------------------------------------+
| name | type | opt. | default | description                              |
+======+======+======+=========+==========================================+
| init | int  | yes  | 0       | The initialization value of the counter. |
+------+------+------+---------+------------------------------------------+

**Result**

Returns the current counter.

**Example**

.. literalinclude:: ../code-samples/plugins/udf/simple.Counter/example.yaml
   :language: YAML