hass.State
^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.udf.hass.State       udf    none         0.14.0
================================ ====== ============ ========

**Description**

Fetches the state of an entity from home assistant by a rest-api call.

**Arguments**

+---------+-------+------+---------+------------------------------------------------------------------------------------+
| name    | type  | opt. | default | description                                                                        |
+=========+=======+======+=========+====================================================================================+
| url     | str   | no   | n/a     | The url to your home assistant instance (e.g. ``http://hass:8123``)                |
+---------+-------+------+---------+------------------------------------------------------------------------------------+
| token   | str   | no   | n/a     | The long lived access token to get access to home assistant                        |
+---------+-------+------+---------+------------------------------------------------------------------------------------+
| timeout | float | yes  | 5.0     | Tell the request to abort the waiting for a response after given number of seconds |
+---------+-------+------+---------+------------------------------------------------------------------------------------+

.. note::

   Create a long lived access token: `Home Assistant documentation <https://developers.home-assistant.io/docs/en/auth_api.html#long-lived-access-token>`_

**Call Arguments**

+-----------+------+------+---------+-------------------------------------------------------------------------------------------------------------------------+
| name      | type | opt. | default | description                                                                                                             |
+===========+======+======+=========+=========================================================================================================================+
| entity_id | str  | no   | n/a     | The entity to fetch the state                                                                                           |
+-----------+------+------+---------+-------------------------------------------------------------------------------------------------------------------------+
| attribute | str  | yes  | None    | Optionally you can fetch the state of one of the entity attributes. Not passed will fetch the state of the entity       |
+-----------+------+------+---------+-------------------------------------------------------------------------------------------------------------------------+

**Result**

Returns the current state of the entity or one of it's attributes. If the entity is not known to home assistant an exception is raised.
In case of an attribute does not exists, ``None`` will be returned instead to signal it's absence.


**Example**

.. literalinclude:: ../code-samples/plugins/udf/hass.State/example.yaml
   :language: YAML