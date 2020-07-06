fitbit.Devices
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.fitbit.Devices  poll   fitbit       0.13.0
================================ ====== ============ ========

**Description**

Requests details about your fitbit devices / trackers (battery, model, ...) associated to your account.

Please see `Fitbit Authentication`_ to configure to prepare your account accordingly.

**Arguments**

+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
| name      | type      | opt. | default | description                                                                                                                               |
+===========+===========+======+=========+===========================================================================================================================================+
| config    | str       | no   | n/a     | The configuration file that keeps your initial and refreshed authentication tokens (see `Fitbit Authentication`_ for detailed information)|
+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
| system    | str       | yes  | None    | The metric system to use based on your localisation (de_DE, en_US, ...). Default is your configured metric system in your fitbit account  |
+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

Emits a list that contains your available trackers and/or devices and their associated details:


.. code-block:: python

   [{
     "battery": "Empty",
     "battery_level": 10,
     "device_version": "Charge 2",
     "features": [],
     "id": "abc",
     "last_sync_time": "2018-12-23T10:47:40.000",
     "mac": "AAAAAAAAAAAA",
     "type": "TRACKER"
   }, {
     "battery": "High",
     "battery_level": 95,
     "device_version": "Blaze",
     "features": [],
     "id": "xyz",
     "last_sync_time": "2019-01-02T10:48:39.000",
     "mac": "FFFFFFFFFFFF",
     "type": "TRACKER"
   }]

**Example**

.. literalinclude:: ../code-samples/plugins/pull/fitbit.Devices/example.yaml
   :language: YAML