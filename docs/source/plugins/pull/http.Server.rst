http.Server
^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.http.Server     pull   none         < 0.10.0
================================ ====== ============ ========

**Description**

Creates a specific route on the builtin api server and listens to any call to that route.
Any data passed to the endpoint will be tried to be parsed to a dictionary (json).
If this is not possible the data will be passed as is. See sections ``Result`` for specific payload and examples.

**Arguments**

+-----------------+-----------+------+---------+------------------------------------------------------------------------------------------------------------+
| name            | type      | opt. | default | description                                                                                                |
+=================+===========+======+=========+============================================================================================================+
| prefix_path     | str       | no   | n/a     | The route to create for incoming traffic on the builtin api server. See the Example section for reference. |
+-----------------+-----------+------+---------+------------------------------------------------------------------------------------------------------------+
| allowed_methods | List[str] | yes  | GET     | List of http methods that are allowed. Default is 'GET'.                                                   |
+-----------------+-----------+------+---------+------------------------------------------------------------------------------------------------------------+


**Result**

Assumes that you configured your pull with `prefix_path = callme`

.. code-block:: shell

   curl -X GET "http://localhost:9999/callme/telephone/now?number=12345&priority=high" --data '{"magic": 42}'


.. code-block:: python

   {
     "endpoint": "telephone/now",
     "data": {"magic": 42},
     "levels": ["telephone", "now"],
     "method": "GET",
     "query": {"number": "12345", "priority": "high"},
     "is_json": True,
     "url": "http://localhost:9999/callme/telephone/now?number=12345&priority=high",
     "full_path": "/callme/telephone/now?number=12345&priority=high",
     "path": "/callme/telephone/now"
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/http.Server/example.yaml
   :language: YAML