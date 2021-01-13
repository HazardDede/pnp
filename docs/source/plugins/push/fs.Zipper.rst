fs.Zipper
^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.push.fs.Zipper       push   none         0.21.0
================================ ====== ============ ========

**Description**

The push expects a directory or a file path to be passed as the payload.
As long it's a valid path it will zip the directory or the single file and return
the absolute path to the created zip file.

.. NOTE::

   You can use a so called ``.zipignore`` file to exclude files and directories from zipping.
   It works - mostly - like a ``.gitignore`` file.
   To use a ``.zipignore`` file you have to put it in the root the folder you want to zip.
   An example ``.zipignore`` looks like this:

   .. code:: text

      __pycache__/
      *.log

   This example will ignore all folder called ``__pycache__`` and all files with the extension ``.log``

**Arguments**

+--------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------+
| name         | type | opt. | default | env | description                                                                                                                                     |
+==============+======+======+=========+=====+=================================================================================================================================================+
| source       | str  | yes  | n/a     | yes | Specifies the source directory or file to zip. If not passed the source can be specified by the envelope at runtime.                            |
+--------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------+
| out_path     | str  | yes  | tmp     | no  | Specifies the path to the general output path where all target zip files should be generated. If not passed the systems temp directory is used. |
+--------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------+
| archive_name | str  | yes  | below   | yes | Explicitly specifies the name of the resulting archive.                                                                                         |
+--------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------+

The default of ``archive_name`` will be either the original file name (if you zip a single file)
resp. the name of the zipped directory (if you zip a directory).
In both cases the extension ``.zip`` will be added.
If you do not want an extension, you have to provide the ``archive_name``.


**Result**

Will return an absolute path to the zip file created.

**Example**

.. literalinclude:: ../code-samples/plugins/push/fs.Zipper/example.yaml
   :language: YAML

The next example is useful for dynamically adjusting the archive name to generate
unique names for storing multiple backups:

.. literalinclude:: ../code-samples/plugins/push/fs.Zipper/example_backup.yaml
   :language: YAML
