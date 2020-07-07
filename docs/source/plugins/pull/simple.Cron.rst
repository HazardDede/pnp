simple.Cron
^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.simple.Cron     pull   none         0.16.0
================================ ====== ============ ========

**Description**

Execute push-components based on time constraints configured by cron-like expressions.

This plugin basically wraps `cronex <https://pypi.org/project/cronex/>`_ to parse cron expressions and to check if
any job is pending. See the documentation of ``cronex`` for a guide on featured/supported cron expressions.


**Arguments**

+-------------+-----------+------+---------+---------------------------------------------------+
| name        | type      | opt. | default | description                                       |
+=============+===========+======+=========+===================================================+
| exppresions | List[str] | no   | n/a     | Cron like expressions to configure the scheduler. |
+-------------+-----------+------+---------+---------------------------------------------------+

**Result**

Imagine your cron expressions looks like this: ``*/1 * * * * every minute``.
The pull will emit the text ``every minute`` every minute.

**Example**

.. literalinclude:: ../code-samples/plugins/pull/simple.Cron/example.yaml
   :language: YAML