simple.RunOnce
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.simple.RunOnce  pull   none         0.23.0
================================ ====== ============ ========

**Description**

Takes a valid ``plugins.pull.Polling`` component and immediately executes it and ventures
down the given ``plugins.push`` components. If no component to wrap is given it will simple execute the
push chain.

**Arguments**

+------+--------+------+---------+--------------------------------------------------------------------------------------------+
| name | type   | opt. | default | description                                                                                |
+======+========+======+=========+============================================================================================+
| poll | plugin | yes  | None    | The polling component you want to run once. If not passed the push chain will be executed. |
+------+--------+------+---------+--------------------------------------------------------------------------------------------+

**Result**

Emits the payload of the polling component if given. Otherwise an empty dictionary will be returned.

**Example**

.. literalinclude:: ../code-samples/plugins/pull/simple.RunOnce/example.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/pull/simple.RunOnce/example_wrapped.yaml
   :language: YAML