zway.ZwayReceiver
^^^^^^^^^^^^^^^^^

=================================== ====== ============ ========
plugin                              type   extra        version
=================================== ====== ============ ========
pnp.plugins.pull.zway.ZwayReceiver  pull   none         0.11.0
=================================== ====== ============ ========

**Description**

Setup a route /zway on the builtin api server to process incoming GET requests from the Zway app `HttpGet <https://github.com/hplato/Zway-HTTPGet/blob/master/index.js>`_

.. NOTE::

   * You have to configure your HttpGET app with the ``URL to get`` set to ``http://<host>:<port>/zway?device=%DEVICE%&value=%value%``
   * You need to enable the api via configuration to make this work.

**Arguments**

+------------------------+------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name                   | type | opt. | default | description                                                                                                                                                                                                                                                                                                                           |
+========================+======+======+=========+=======================================================================================================================================================================================================================================================================================================================================+
| mode                   | str  | yes  | mapping | If set to ``mapping`` (default) you should provide the ``device_mapping`` to manually map your virtual devices. If set to ``auto`` the plugin will try to determine the device_id, command class, mode and the type on it's own. If set to ``both`` the plugin will first try the ``device_mapping`` and then perform the auto-magic. |
+------------------------+------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| device_mapping         | Dict | yes  | None    | A mapping to map the somewhat cryptic virtual device names to human readable ones. Default is None, which means that no mapping will be performed. Two ways possible:                                                                                                                                                                 |
|                        |      |      |         |                                                                                                                                                                                                                                                                                                                                       |
|                        |      |      |         | * Ordinary mapping from ``virtual device name`` -> ``alias``.                                                                                                                                                                                                                                                                         |
|                        |      |      |         |                                                                                                                                                                                                                                                                                                                                       |
|                        |      |      |         | * Enhanced mapping from ``virtual device name`` -> ``dictionary with properties``. One property has to be ``alias``.                                                                                                                                                                                                                  |
+------------------------+------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ignore_unknown_devices | str  | yes  | False   | If set to True all incoming requests that are associated with a device that is not part of the mapping or - when mode = ``[auto, both]`` - cannot be auto mapped will be ignored.                                                                                                                                                     |
+------------------------+------+------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

Issuing ``curl -X GET "http://<ip>:<port>/zway?device=vdevice1&value=5.5"`` and the device_mapping ``vdevice1 -> alias of vdevice1`` the emitted message will look like this:

.. code-block:: python

   {
     "device_name": "alias of vdevice1",
     "raw_device": "vdevice1"
     "value": "5.5",
     "props": {}
   }

When ``mode`` is ``auto`` or ``both`` the plugin will try to determine the device id and the type of the virtual device on it's
own. Given the virtual device name ``ZWayVDev_zway_7-0-48-1`` and the value of ``on`` will produce the following:


.. code-block:: python

   {
     "device_name": "7",
     "raw_device": "ZWayVDev_zway_7-0-48-1",
     "value": "on"
     "props": {
       "command_class": "48",
       "mode": "1",
       "type": "motion"
     }
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/zway.ZwayReceiver/example.yaml
   :language: YAML