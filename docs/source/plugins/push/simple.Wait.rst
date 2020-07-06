simple.Wait
^^^^^^^^^^^

============================= ====== ============ ========
plugin                        type   extra        version
============================= ====== ============ ========
pnp.plugins.push.simple.Wait  push   none         0.19.0
============================= ====== ============ ========

**Description**

Performs a sleep operation and waits for some time to pass by.

**Arguments**

+----------+-----------+------+---------+-----+------------------------------------------------------------------------------------------------------------------------+
| name     | type      | opt. | default | env | description                                                                                                            |
+==========+===========+======+=========+=====+========================================================================================================================+
| wait_for | float|str | no   | n/a     | no  | The time to wait for before proceeding.                                                                                |
|          |           |      |         |     | You can pass literals such as ``5s``, ``1m``; ints such as ``1``, ``2``, ``3`` or floats such as ``0.5``.              |
|          |           |      |         |     | In the end everything will be converted to it's float representation (``1 => 1.0; 5s => 5.0; 1m => 60.0; 0.5 => 0.5``) |
+----------+-----------+------+---------+-----+------------------------------------------------------------------------------------------------------------------------+

**Result**

Will return the payload as it is for easy chaining of dependencies.

**Example**

.. literalinclude:: ../code-samples/plugins/push/simple.Wait/example.yaml
   :language: YAML
