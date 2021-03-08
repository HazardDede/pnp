io.FSWatcher
^^^^^^^^^^^^^^^^^^^^

====================================== ====== ============ ========
plugin                                 type   extra        version
====================================== ====== ============ ========
pnp.plugins.pull.io.FSWatcher          pull   fswatcher    < 0.10.0
====================================== ====== ============ ========

**Description**

Watches the given directory for changes like created, moved, modified and deleted files.

Per default will recursively report any file that is touched, changed or deleted in the given path. The
directory itself or subdirectories will be object to reporting too, if ``ignore_directories`` is set to ``False``.

**Arguments**

+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name               | type      | opt. | default | description                                                                                                                                                         |
+====================+===========+======+=========+=====================================================================================================================================================================+
| path               | str       | no   | n/a     | The path to track for file / directory changes                                                                                                                      |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| recursive          | bool      | yes  | True    | If set to True, any subfolders of the given path will be tracked too.                                                                                               |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| patterns           | List[str] | yes  | None    | Any file pattern (e.g. `*`.txt or `*`.txt, `*`.md. If set to None no filter is applied.                                                                             |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ignore_patterns    | List[str] | yes  | None    | Any patterns to ignore (specify like argument ``patterns``). If set to None, nothing will be ignored.                                                               |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ignore_directories | bool      | yes  | False   | If set to True will send events for directories when file change.                                                                                                   |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| case_sensitive     | bool      | yes  | False   | If set to True, any pattern is case_sensitive, otherwise it is case insensitive.                                                                                    |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| events             | List[str] | yes  | None    | The events to track. One or multiple of 'moved', 'deleted', 'created' and/or 'modified'. If set to None all events will be reported.                                |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| load_file          | bool      | yes  | False   | If set to True the file contents will be loaded into the result.                                                                                                    |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| mode               | str       | yes  | auto    | Open mode of the file (only necessary when load_file is True). Can be text, binary or auto (guessing).                                                              |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| base64             | bool      | yes  | False   | If set to True the loaded file contents will be converted to base64 (only applicable when load_file is True). Argument `mode` will be automatically set to 'binary' |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| defer_modified     | float     | yes  | 0.5     | There might be multiple flushes of a file before it is written completely to disk. Without defer_modified each flush will raise a modified event.                   |
+--------------------+-----------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

Example of an emitted message:


.. code-block:: python

   {
       "operation": "modified",
       "source": "/tmp/abc.txt",
       "is_directory": False,
       "destination": None,  # Only non-None when operation = "moved"
       "file": {  # Only present when load_file is True
           "file_name": "abc.txt",
           "content": "foo and bar",
           "read_mode": "text",
           "base64": False
       }
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/io.FSWatcher/example.yaml
   :language: YAML