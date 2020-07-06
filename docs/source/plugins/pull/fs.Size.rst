fs.Size
^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.fs.Size         poll   none         0.17.0
================================ ====== ============ ========

**Description**

Periodically determines the size of the specified files or directories in bytes.

**Arguments**

+---------------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name          | type      | opt. | default | description                                                                                                                                                                                           |
+===============+===========+======+=========+=======================================================================================================================================================================================================+
| paths         | List[str] | no   | n/a     | List of files and/or directories to monitor their sizes in bytes.                                                                                                                                     |
+---------------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fail_on_error | bool      | yes  | True    | If set to true, the plugin will raise an error when a file/directory does not exists or any other file system related error occurs. Otherwise the plugin will proceed and simply report None as size. |
+---------------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. NOTE::

   Be careful when adding directories with a large amount of files. This will be prettly slow cause
   the plugin will iterate over each file and determine it's individual size.

**Result**

Example of an emitted message. Size is in bytes.

.. code-block:: python

   {
     "logs": 32899586,
     "copy": 28912
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/fs.Size/example.yaml
   :language: YAML