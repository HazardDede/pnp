io.FSSize
^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.io.FSSize       poll   none         0.17.0
================================ ====== ============ ========

**Description**

Periodically determines the size of the specified files or directories in bytes.

**Arguments**

+---------------+-----------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name          | type            | opt. | default | description                                                                                                                                                                                           |
+===============+=================+======+=========+=======================================================================================================================================================================================================+
| paths         | Dict[str, path] | no   | n/a     | Mapping of files and/or directories (values) to monitor their sizes in bytes using an alias (keys). Alternative use a list of files/directories. The alias will be the basename of the file/directory.|
+---------------+-----------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fail_on_error | bool            | yes  | True    | If set to true, the plugin will raise an error when a file/directory does not exists or any other file system related error occurs. Otherwise the plugin will proceed and simply report None as size. |
+---------------+-----------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

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

.. literalinclude:: ../code-samples/plugins/pull/io.FSSize/example.yaml
   :language: YAML