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

+---------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------+
| name    | type | opt. | default | env | description                                                                                                                                     |
+=========+======+======+=========+=====+=================================================================================================================================================+
| source  | str  | yes  | n/a     | yes | Specifies the source directory or file to zip. If not passed the source can be specified by the envelope at runtime.                            |
+---------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------+
| out_dir | str  | yes  | tmp     | no  | Specifies the path to the general output path where all target zip files should be generated. If not passed the systems temp directory is used. |
+---------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

Will return an absolute path to the zip file created.

**Example**

.. literalinclude:: ../code-samples/plugins/push/fs.Zipper/example.yaml
   :language: YAML
