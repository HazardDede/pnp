simple.Count
^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.simple.Count    poll   none         < 0.10.0
================================ ====== ============ ========

**Description**

Emits every ``interval`` seconds a counting value which runs from ``from_cnt`` to ``to_cnt``.
If ``to_cnt``  is None the counter will count to infinity (or more precise to ``sys.maxsize``).

**Arguments**

+----------+------+------+-------------+--------------------------------------------------------------------------------------+
| name     | type | opt. | default     | description                                                                          |
+==========+======+======+=============+======================================================================================+
| from_cnt | int  | yes  | 0           | Starting value of the counter.                                                       |
+----------+------+------+-------------+--------------------------------------------------------------------------------------+
| to_cnt   | int  | yes  | sys.maxsize | End value of the counter. If not passed set to "infinity" (precise: ``sys.maxsize``) |
+----------+------+------+-------------+--------------------------------------------------------------------------------------+

**Result**

Counter value (int).


**Example**

.. literalinclude:: ../code-samples/plugins/pull/simple.Count/example.yaml
   :language: YAML