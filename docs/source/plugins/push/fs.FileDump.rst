fs.FileDump
^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.push.fs.FileDump     push   none         < 0.10.0
================================ ====== ============ ========

**Description**

This push dumps the given ``payload`` to a file to the specified ``directory``.
If argument ``file_name`` is ``None``, a name will be generated based on the current datetime (``%Y%m%d-%H%M%S``).
If ``file_name`` is not passed (or ``None``) you should pass ``extension`` to specify the extension of the generated
file name.
Argument ``binary_mode`` controls whether the dump is binary (``mode=wb``) or text (``mode=w``).


**Arguments**

+-------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+
| name        | type | opt. | default | env | description                                                                                      |
+=============+======+======+=========+=====+==================================================================================================+
| directory   | str  | yes  | . (cwd) | no  | The target directory to store the dumps.                                                         |
+-------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+
| file_name   | str  | yes  | None    | yes | The name of the file to dump. If not passed a file name will be automatically generated.         |
+-------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+
| extension   | str  | yes  | .dump   | yes | The extension to use when the file name is automatically generated.                              |
+-------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+
| binary_mode | bool | yes  | False   | no  | If set to True the file will be written in binary mode (``wb``); otherwise in text mode (``w``). |
+-------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+

**Result**

Will return an absolute path to the file created.

**Example**

.. literalinclude:: ../code-samples/plugins/push/fs.FileDump/example1.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/push/fs.FileDump/example2.yaml
   :language: YAML
