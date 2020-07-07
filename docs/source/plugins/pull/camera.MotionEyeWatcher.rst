camera.MotionEyeWatcher
^^^^^^^^^^^^^^^^^^^^^^^

========================================= ====== ============ ========
plugin                                    type   extra        version
========================================= ====== ============ ========
pnp.plugins.pull.camera.MotionEyeWatcher  pull   fswatcher    0.16.0
========================================= ====== ============ ========

**Description**

Watches a motioneye directory (where the images and the movies get persisted from motioneye) to trigger some useful events
based on new / modified files. The motion event only works, when the camera is configured to persist images / movies
only when som motion is triggered and not 24/7.

For example I use this plugin to publish a binary motion sensor via mqtt discovery to home assistant and upload the
images and videos to dropbox and notify me via home assistant notifications.

**Arguments**

+------------------+----------+------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name             | type     | opt. | default | description                                                                                                                                                                                                                                                  |
+==================+==========+======+=========+==============================================================================================================================================================================================================================================================+
| path             | str      | no   | n/a     | The motioneye media directory to watch                                                                                                                                                                                                                       |
+------------------+----------+------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| image_ext        | str      | yes  | jpg     | The file extension of your image files. Deactivate by passing ``None``                                                                                                                                                                                       |
+------------------+----------+------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| movie_ext        | str      | yes  | mp4     | The file extension of your movie files. Deactivate by passing ``None``                                                                                                                                                                                       |
+------------------+----------+------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| motion_cool_down | duration | yes  | 30s     | Based on created/modified files a motion event might be triggered. After the specified time duration without motion, the ``motion off`` event will be triggered                                                                                              |
+------------------+----------+------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| defer_modified   | float    | yes  | 0.5     | If set greater than 0, it will defer the sending of modified events for that amount of time in seconds. There might be multiple flushes of a file before it is written completely to disk. Without ``defer_modified`` each flush will raise a modified event |
+------------------+----------+------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

Example of a new movie file:

.. code-block:: python

   {
     "event": "movie",
     "source": "abs/path/to/the/movie/file.mp4"
   }

Example of a new image file:

.. code-block:: python

   {
     "event": "image",
     "source": "abs/path/to/the/image/file.jpg"
   }


Example of a new motion on/off event:

.. code-block:: python

   {
     "event": "motion",
     "state": "on"  # or "off"
   }


**Example**

.. literalinclude:: ../code-samples/plugins/pull/camera.MotionEyeWatcher/example.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/pull/camera.MotionEyeWatcher/example2.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/pull/camera.MotionEyeWatcher/push_camera.sh
   :language: shell