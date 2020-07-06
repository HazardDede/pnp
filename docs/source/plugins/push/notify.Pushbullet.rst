notify.Pushbullet
^^^^^^^^^^^^^^^^^

=================================== ====== ============ ========
plugin                              type   extra        version
=================================== ====== ============ ========
pnp.plugins.push.notify.Pushbullet  push   pushbullet   0.12.0
=================================== ====== ============ ========

**Description**

Sends a message to the `Pushbullet <http://www.pushbullet.com>`_ service.
The type of the message will be guessed:

* ``push_link`` for a single http link
* ``push_file`` if the link is directed to a file (mimetype will be guessed)
* ``push_note`` for everything else (converted to ``str``)

**Arguments**

+---------+------+------+---------+-----+-----------------------------------------+
| name    | type | opt. | default | env | description                             |
+=========+======+======+=========+=====+=========================================+
| api_key | str  | no   | n/a     | no  | The api key to your pushbullet account. |
+---------+------+------+---------+-----+-----------------------------------------+
| title   | str  | yes  | pnp     | no  | The title to use for all messages.      |
+---------+------+------+---------+-----+-----------------------------------------+


**Result**

Will return the payload as it is for easy chaining of dependencies.

**Example**

.. literalinclude:: ../code-samples/plugins/push/notify.Pushbullet/example.yaml
   :language: YAML
