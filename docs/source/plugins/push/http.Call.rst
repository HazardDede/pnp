http.Call
^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.push.http.Call       push   none         0.21.0
================================ ====== ============ ========

**Description**

Makes a request to a http resource.

**Arguments**

+------------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name             | type | opt. | default | env | description                                                                                                                                                                                                                                     |
+==================+======+======+=========+=====+=================================================================================================================================================================================================================================================+
| url              | str  | no   | n/a     | yes | Request url.                                                                                                                                                                                                                                    |
+------------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| method           | str  | yes  | GET     | yes | The http method to use for the request. Must be a valid http method (GET, POST, ...).                                                                                                                                                           |
+------------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fail_on_error    | bool | yes  | False   | yes | If True the push will fail on a http status code <> 2xx. This leads to an error message recorded into the logs and no further execution of any dependencies.                                                                                    |
+------------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| provide_response | bool | yes  | False   | no  | If True the push will **not** return the payload as it is, but instead provide the response status_code, fetched url content and a flag if the url content is a json response. This is useful for other push instances in the dependency chain. |
+------------------+------+------+---------+-----+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

Will return the payload as it is for easy chaining of dependencies.
If ``provide_response`` is True the push will return a dictionary that looks like this:

.. code-block:: python

   {
     "status_code": 200,
     "data": "fetched url content",
     "is_json": False
   }

**Example**

.. literalinclude:: ../code-samples/plugins/push/http.Call/example1.yaml
   :language: YAML

.. literalinclude:: ../code-samples/plugins/push/http.Call/example2.yaml
   :language: YAML
