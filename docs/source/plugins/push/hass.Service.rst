hass.Service
^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.push.hass.Service    push   none         0.16.0
================================ ====== ============ ========

**Description**

Calls a home assistant service providing the payload as service-data.

**Arguments**

+---------+-----------+------+---------+-----+-------------------------------------------------------------------------------+
| name    | type      | opt. | default | env | description                                                                   |
+=========+===========+======+=========+=====+===============================================================================+
| url     | str       | no   | n/a     | no  | The url to your home assistant instance (e.g. ``http://hass:8123``)           |
+---------+-----------+------+---------+-----+-------------------------------------------------------------------------------+
| token   | str       | no   | n/a     | no  | The long live access token to get access to home assistant.                   |
+---------+-----------+------+---------+-----+-------------------------------------------------------------------------------+
| domain  | str       | no   | n/a     | no  | The domain of the service to call.                                            |
+---------+-----------+------+---------+-----+-------------------------------------------------------------------------------+
| service | str       | no   | n/a     | no  | The name of the service to call.                                              |
+---------+-----------+------+---------+-----+-------------------------------------------------------------------------------+
| timeout | int|float | yes  | 5.0     | no  | Tell the request to stop waiting for a response after given number of seconds.|
+---------+-----------+------+---------+-----+-------------------------------------------------------------------------------+

.. note::

   Create a long lived access token: `Home Assistant documentation <https://developers.home-assistant.io/docs/en/auth_api.html#long-lived-access-token>`_


**Result**

Returns the payload as-is for better chaining (this plugin can't add any useful information).

**Example**

.. literalinclude:: ../code-samples/plugins/push/hass.Service/example1.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/push/hass.Service/example2.yaml
   :language: YAML

