sensor.Sound
^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.sensor.Sound    pull   sound        0.15.0
================================ ====== ============ ========

**Description**

Listens to the microphone in realtime and searches the stream for specific sound patterns.

Practical example: I use this plugin to recognize my doorbell without tampering with the electrical device ;-)

**Arguments**

+-----------------+------------+------+---------+----------------------------------------------------------------------------------------+
| name            | type       | opt. | default | description                                                                            |
+=================+============+======+=========+========================================================================================+
| wav_files       | List[Dict] | no   | n/a     | See below for a detailed description                                                   |
+-----------------+------------+------+---------+----------------------------------------------------------------------------------------+
| device_index    | int        | yes  | None    | The index of the microphone device. Run ``pnp_record_sound --list`` to get the index.  |
|                 |            |      |         | If not specified pyAudio will try to find a capable device                             |
+-----------------+------------+------+---------+----------------------------------------------------------------------------------------+
| ignore_overflow | bool       | yes  | true    | If set to True any buffer overflows due to slow realtime processing will be ignored.   |
|                 |            |      |         | Otherwise an exception will be thrown and the plugin will abort.                       |
+-----------------+------------+------+---------+----------------------------------------------------------------------------------------+

* **wav_files**

  A list of dictionaries containing the configuration for each file that contains an original sound pattern to listen for.
  Possible keys:

   +----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------+
   | name     | type  | opt. | default | description                                                                                                                 |
   +==========+=======+======+=========+=============================================================================================================================+
   | path     | str   | no   | n/a     | The path to the original sound file. Absolute or relative to the pnp configuration file                                     |
   +----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------+
   | mode     | str   | yes  | pearson | Correlation/similarity method. Default is pearson. Try out which one is best for you                                        |
   +----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------+
   | offset   | float | yes  | 0.0     | Adjusts sensitivity for similarity. Positive means less sensitive; negative is more sensitive. You should try out 0.1 steps |
   +----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------+
   | cooldown | Dict  | yes  | special | See below for a detailed description                                                                                        |
   +----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------+

* **cooldown**

  Contains the cooldown configuration. Default is a cooldown period of 10 seconds and no emit of a cooldown event.
  Possible keys:

   +------------+------+------+---------+-------------------------------------------------------------------------------------+
   | name       | type | opt. | default | description                                                                         |
   +============+======+======+=========+=====================================================================================+
   | period     | str  | yes  | 10s     | Prevents the pull to emit more than one sound detection event per cool down period. |
   +------------+------+------+---------+-------------------------------------------------------------------------------------+
   | emit_event | bool | yes  | false   | If set to true the end of the cooldown period will an emit as well.                 |
   +------------+------+------+---------+-------------------------------------------------------------------------------------+

.. NOTE::

   * You can list your available input devices: ``pnp_record_sound --list``
   * You can record a wav file from an input device: ``pnp_record_sound <out.wav> --seconds=<seconds_to_record> --index=<idx>``
   * This one is _not_ pre-installed when using the docker image. Would be grateful if anyone can integrate it

**Result**

Will emit the event below when the correlation coefficient is above or equal the threshold.
In this case the component has detected a sound that is similar to one of the given sound patterns


.. code-block:: python

   {
     "type": "sound"  # Type 'sound' means we detected a sound pattern
     "sound": ding,  # Name of the wav_file without path and extension. To differentiate if you have multiple patterns you listen to
     "corrcoef": 0.82,  # Correlation coefficient probably between [-1;+1] for pearson
     "threshold": 0.6  # Threshold influenced by sensitivity_offset
   }

Will emit the event below when you have configured the component to send cooldown events as well.


.. code-block:: python

   {
     "type": "cooldown"  # Type 'cooldown' means that we previously identified a sound pattern and the cooldown has happened
     "sound": ding,  # Name of the wav_file without path and extension. To differentiate if you have multiple patterns you listen to
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/sensor.Sound/example.yaml
   :language: YAML