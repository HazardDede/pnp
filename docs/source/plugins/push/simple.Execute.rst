simple.Execute
^^^^^^^^^^^^^^

=================================== ====== ============ ========
plugin                              type   extra        version
=================================== ====== ============ ========
pnp.plugins.push.simple.Execute     push   none         0.12.0
=================================== ====== ============ ========

**Description**

Executes a command with given arguments in a shell of the operating system.
Both ``command`` and ``args`` may include placeholders (e.g. ``{{placeholder}}``) which are injected at runtime
by passing the specified payload after selector transformation. Please see the examples section for further details.

Will return the exit code of the command and optionally the output from stdout and stderr.

**Arguments**

+---------+-----------+------+---------+-----+------------------------------------------------------------------------------------------+
| name    | type      | opt. | default | env | description                                                                              |
+=========+===========+======+=========+=====+==========================================================================================+
| command | str       | no   | n/a     | no  | The command to execute. May contain placeholders.                                        |
+---------+-----------+------+---------+-----+------------------------------------------------------------------------------------------+
| args    | List[str] | yes  | []      | no  | The arguments to pass to the command. Default is no arguments. May contain placeholders. |
+---------+-----------+------+---------+-----+------------------------------------------------------------------------------------------+
| cwd     | str       | yes  | special | no  | Specifies where to execute the command (working directory).                              |
|         |           |      |         |     | Default is the folder where the invoked pnp configuration file is located.               |
+---------+-----------+------+---------+-----+------------------------------------------------------------------------------------------+
| timeout | str|float | yes  | 5s      | no  | Specifies how long the worker should wait for the command to finish.                     |
+---------+-----------+------+---------+-----+------------------------------------------------------------------------------------------+
| capture | bool      | yes  | False   | no  | If ``True`` stdout and stderr output is captured, otherwise not.                         |
+---------+-----------+------+---------+-----+------------------------------------------------------------------------------------------+

**Result**

Returns a dictionary that contains the ``return_code`` and optionally the output from ``stdout`` and ``stderr`` whether
``capture`` is set or not. The output is a list of lines.

.. code-block:: python

   {
     "return_code": 0
     "stdout": ["hello", "dude!"]
     "stderr": []
   }

**Example**

.. literalinclude:: ../code-samples/plugins/push/simple.Execute/example1.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/push/simple.Execute/example2.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/push/simple.Execute/example3.yaml
   :language: YAML
