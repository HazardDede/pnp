simple.Nop
^^^^^^^^^^

============================= ====== ============ ========
plugin                        type   extra        version
============================= ====== ============ ========
pnp.plugins.push.simple.Nop   push   none         < 0.10.0
============================= ====== ============ ========

**Description**

Executes no operation at all. A call to push(...) just returns the payload.
This push is useful when you only need the power of the selector for dependent pushes.

See the example section for an example.

Nop = No operation OR No push ;-)

**Result**

Will return the payload as it is for easy chaining of dependencies.

**Example**

.. literalinclude:: ../code-samples/plugins/push/simple.Nop/example.yaml
   :language: YAML
