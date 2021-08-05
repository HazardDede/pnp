net.FTPServer
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.net.FTPServer   pull   ftp          0.17.0
================================ ====== ============ ========

**Description**

Runs a ftp server on the specified port to receive and send files by ftp protocol.

Optionally sets up a simple user/password authentication mechanism.

**Arguments**

+-------------+------------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name        | type             | opt. | default | description                                                                                                                                                                                                 |
+=============+==================+======+=========+=============================================================================================================================================================================================================+
| directory   | str              | yes  | None    | The directory to serve via ftp protocol. If not given a directory is created is created temporarily to accept incoming uploads.                                                                             |
+-------------+------------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| port        | int              | yes  | 2121    | The port to listen on.                                                                                                                                                                                      |
+-------------+------------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| user_pwd    | str / Tuple[str] | yes  | None    | User/password combination (as a tuple/list; see example). You may specify the user only - password will be empty OR you can enable anonymous access by not providing the argument.                          |
+-------------+------------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| events      | List[str]        | yes  | None    | A list of events to subscribe to. Available events are: connect, disconnect, login, logout, file_received, file_sent, file_received_incomplete, file_sent_incomplete. By default all events are subscribed. |
+-------------+------------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| max_cons    | int              | yes  | 256     | The maximum number of simultaneous connections the ftpserver will permit.                                                                                                                                   |
+-------------+------------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| max_cons_ip | int              | yes  | 5       | The maximum number of simultaneous connections from the same ip. Default is 5.                                                                                                                              |
+-------------+------------------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


**Result**

All emitted messages will have an event field to identify the type of the event and an - optional - data field.

The data field will contain the user for login/logout events and the file_path for file-related events.

.. code-block:: python

   {
     "event": "file_received",
     "data": {
       "file_path": "/private/tmp/ftp/test.txt"
     }
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/net.FTPServer/example.yaml
   :language: YAML