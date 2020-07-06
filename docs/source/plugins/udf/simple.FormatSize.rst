simple.FormatSize
^^^^^^^^^^^^^^^^^

================================= ====== ============ ========
plugin                            type   extra        version
================================= ====== ============ ========
pnp.plugins.udf.simple.FormatSize udf    none         0.14.0
================================= ====== ============ ========

**Description**

Returns the size of a file (or whatever) as a human readable size (e.g. bytes, KB, MB, GB, TB, PB).
The input is expected to be at byte scale.

**Call Arguments**

+---------------+-----------+------+---------+---------------------------------------------------------+
| name          | type      | opt. | default | description                                             |
+===============+===========+======+=========+=========================================================+
| size_in_bytes | int|float | no   | n/a     | The size in bytes to format to a human readable format. |
+---------------+-----------+------+---------+---------------------------------------------------------+

**Result**

Returns the argument in a human readable size format.

**Example**

.. literalinclude:: ../code-samples/plugins/udf/simple.FormatSize/example.yaml
   :language: YAML