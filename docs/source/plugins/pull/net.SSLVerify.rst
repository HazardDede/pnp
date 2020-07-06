net.SSLVerify
^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.net.SSLVerify   poll   none         0.22.0
================================ ====== ============ ========

**Description**

Periodically checks if the ssl certificate of a given host is valid and how many days are remaining before the certificate will expire.

**Arguments**

+---------+-------+------+---------+---------------------------------------------+
| name    | type  | opt. | default | description                                 |
+=========+=======+======+=========+=============================================+
| host    | str   | no   | n/a     | The host to check for it's SSL certificate. |
+---------+-------+------+---------+---------------------------------------------+
| timeout | float | yes  | 3.0     | Timeout for remote operation.               |
+---------+-------+------+---------+---------------------------------------------+

**Result**

.. code-block:: python

   {
     # Envelope
     "host": "www.google.com",
     "payload": {
       "expires_days": 50,  # Remaining days before expiration
       "expires_at": datetime.datetime(2020, 5, 26, 9, 45, 52),  # Python datetime of expiration
       "expired": False  # True of the certificate is expired; otherwise False.
     }
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/net.SSLVerify/example.yaml
   :language: YAML