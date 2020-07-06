ml.FaceR
^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.push.ml.FaceR        push   faceR        < 0.10.0
================================ ====== ============ ========

**Description**

FaceR (short one for face recognition) tags known faces in images. Output is the image with all faces tagged whether
with the known name or an ``unknown_label``. Default for unknown ones is ``Unknown``.

Known faces can be ingested either by a directory of known faces (``known_faces_dir``) or by mapping of ``known_faces``
(dictionary: name -> [list of face files]).

The ``payload`` passed to the ``push`` method is expected to be a valid byte array that represents an image in memory.
Please see the example section for loading physical files into memory.

.. NOTE::

   This one is **not** pre-installed when using the docker image.
   Would be grateful if anyone can integrate it


**Arguments**

+-----------------+----------------+------+---------+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name            | type           | opt. | default | env | description                                                                                                                                                                       |
+=================+================+======+=========+=====+===================================================================================================================================================================================+
| known_faces     | Dict[str, str] | yes  | None    | no  | Mapping of a person's name to a list of images that contain the person's face.                                                                                                    |
+-----------------+----------------+------+---------+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| known_faces_dir | str            | yes  | None    | no  | A directory containing images with known persons (file_name -> person's name).                                                                                                    |
+-----------------+----------------+------+---------+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| unknown_label   | str            | yes  | Unknown | no  | Tag label of unknown faces.                                                                                                                                                       |
+-----------------+----------------+------+---------+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| lazy            | bool           | yes  | False   | no  | If set to True the face encodings will be loaded when the first push is executed (lazy); otherwise the encodings are loaded when the plugin is initialized (during ``__init__``). |
+-----------------+----------------+------+---------+-----+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. NOTE::

   You need to specify either ``known_faces`` **or** ``known_faces_dir``

**Result**

Will return a dictionary that contains the bytes of the tagged image (key ``tagged_image``) and metadata (``no_of_faces``,
``known_faces``)

.. code-block:: python

   {
     'tagged_image': <bytes of tagged image>
     'no_of_faces': 2
     'known_faces': ['obama']
   }

**Example**

.. literalinclude:: ../code-samples/plugins/push/ml.FaceR/example.yaml
   :language: YAML
