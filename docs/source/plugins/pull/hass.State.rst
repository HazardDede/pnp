hass.State
^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.hass.State      pull   none         0.14.0
================================ ====== ============ ========

**Description**

Connects to the ``home assistant`` websocket api and listens for state changes. If no ``include`` or ``exclude`` is defined
it will report all state changes. If ``include`` is defined only entities that match one of the specified patterns will
be emitted. If ``exclude`` if defined entities that match at least one of the specified patterns will be ignored. ``exclude``
patterns overrides ``include`` patterns.

**Arguments**

+---------+-----------+------+---------+-----------------------------------------------------------------------------------------------------------------------+
| name    | type      | opt. | default | description                                                                                                           |
+=========+===========+======+=========+=======================================================================================================================+
| host    | str       | no   | n/a     | Url to your **home assistant** instance (e.g. ``http://my-hass:8123``)                                                |
+---------+-----------+------+---------+-----------------------------------------------------------------------------------------------------------------------+
| token   | str       | no   | n/a     | Your long lived access token to access the websocket api. See below for further instructions                          |
+---------+-----------+------+---------+-----------------------------------------------------------------------------------------------------------------------+
| include | List[str] | yes  | n/a     | Patterns of entity state changes to include. All state changes that do not match the defined patterns will be ignored |
+---------+-----------+------+---------+-----------------------------------------------------------------------------------------------------------------------+
| exclude | List[str] | yes  | n/a     | Patterns of entity state changes to exclude. All state changes that do match the defined patterns will be ignored     |
+---------+-----------+------+---------+-----------------------------------------------------------------------------------------------------------------------+

.. NOTE::

   * ``include`` and ``exclude`` support wildcards (e.g ``*`` and ``?``)
   * ``exclude`` overrides ``include``. So you can `include` everything from a domain (``sensor.*``) but exclude individual entities.
   * Create a long lived access token: `Home Assistant documentation <https://developers.home-assistant.io/docs/en/auth_api.html#long-lived-access-token>`_

**Result**

The emitted result always contains the `entity_id`, `new_state` and `old_state`:

.. code-block:: python

   {
     "entity_id": "light.bedroom_lamp",
     "old_state": {
       "state": "off",
       "attributes": {},
       "last_changed": "2019-01-08T18:24:42.087195+00:00",
       "last_updated": "2019-01-08T18:40:40.011459+00:00"
     },
     "new_state": {
       "state": "on",
       "attributes": {},
       "last_changed": "2019-01-08T18:41:06.329699+00:00",
       "last_updated": "2019-01-08T18:41:06.329699+00:00"
     }
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/hass.State/example.yaml
   :language: YAML