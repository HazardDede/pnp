simple.Memory
^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.udf.simple.Memory    udf    none         0.14.0
================================ ====== ============ ========

**Description**

Returns a previously memorized value when called.

**Arguments**

+------+------+------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| name | type | opt. | default | description                                                                                                                                        |
+======+======+======+=========+====================================================================================================================================================+
| init | Any  | yes  | None    | The initial memory of the plugin. When not set initially the first call will return the value of ``new_memory``, if specified; otherwise ``None``. |
+------+------+------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------+

**Call Arguments**

+------------+------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
| name       | type | opt. | default | description                                                                                                                                         |
+============+======+======+=========+=====================================================================================================================================================+
| new_memory | Any  | no   | None    | After emitting the current memorized value the current memory is overwritten by this value. Will only be overwritten if the parameter is specified. |
+------------+------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

Returns the memorized value.

**Example**

.. literalinclude:: ../code-samples/plugins/udf/simple.Memory/example.yaml
.. literalinclude:: ../code-samples/plugins/udf/simple.Memory/example.yaml
   :language: YAML