storage.Dropbox
^^^^^^^^^^^^^^^

=================================== ====== ============ ========
plugin                              type   extra        version
=================================== ====== ============ ========
pnp.plugins.push.storage.Dropbox    push   dropbox       0.12.0
=================================== ====== ============ ========

**Description**

Uploads a provided file to the configured dropbox account.

**Arguments**

+---------------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+
| name                | type | opt. | default | env | description                                                                                      |
+=====================+======+======+=========+=====+==================================================================================================+
| api_key             | str  | no   | n/a     | no  | The api key to your dropbox account/app.                                                         |
+---------------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+
| target_file_name    | str  | yes  | None    | yes | The file path on the server where to upload the file to.                                         |
|                     |      |      |         |     | If not specified you have to specify this argument during runtime by setting it in the envelope. |
+---------------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+
| created_shared_link | bool | yes  | True    | no  | If set to ``True``, the push will create a publicly available link to your uploaded file.        |
+---------------------+------+------+---------+-----+--------------------------------------------------------------------------------------------------+

**Result**

Returns a dictionary that contains metadata information about your uploaded file. If you uploaded a file named ``42.txt``,
your result will be similar to the one below:

.. code-block:: python

   {
     "name": "42.txt",
     "id": "HkdashdasdOOOOOadss",
     "content_hash": "aljdhfjdahfafuhu489",
     "size": 42,
     "path": "/42.txt",
     "shared_link": "http://someserver/tosomestuff/asdasd?dl=1",
     "raw_link": "http://someserver/tosomestuff/asdasd?raw=1"
   }


``shared_link`` is the one that is publicly available (but only if you know the link).
Same for ``raw_link``, but this link will return the raw file (without the dropbox overhead).

Both are ``None`` if ``create_shared_link`` is set to ``False``.

**Example**

.. literalinclude:: ../code-samples/plugins/push/storage.Dropbox/example.yaml
   :language: YAML
