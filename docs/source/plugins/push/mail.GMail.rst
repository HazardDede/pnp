mail.GMail
^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.push.mail.GMail      push   gmail        0.15.0
================================ ====== ============ ========

**Description**

Sends an e-mail via the gmail api.

Please see `GMail Token Generation`_ to configure to prepare your account accordingly.

**Arguments**

+------------+---------------+------+---------+-----+-------------------------------------------------------------------------------------------------------------+
| name       | type          | opt. | default | env | description                                                                                                 |
+============+===============+======+=========+=====+=============================================================================================================+
| token_file | str           | no   | n/a     | no  | The file that contains your tokens.                                                                         |
+------------+---------------+------+---------+-----+-------------------------------------------------------------------------------------------------------------+
| recipient  | str|List[str] | no   | n/a     | yes | The recipient (to) of the e-mail. Optionally you can pass a list for multiple recipients.                   |
+------------+---------------+------+---------+-----+-------------------------------------------------------------------------------------------------------------+
| subject    | str           | yes  | None    | yes | Sets the subject of the e-mail. If not passed means that the subject is expected to be set by the envelope. |
+------------+---------------+------+---------+-----+-------------------------------------------------------------------------------------------------------------+
| sender     | str           | yes  | pnp     | yes | Sets the sender of the e-mail.                                                                              |
+------------+---------------+------+---------+-----+-------------------------------------------------------------------------------------------------------------+
| attachment | str           | yes  | None    | yes | Argument value should point to a valid file to attach it to the e-mail. If not passed no file is attached.  |
+------------+---------------+------+---------+-----+-------------------------------------------------------------------------------------------------------------+

**Result**

Will return the payload as it is for easy chaining of dependencies.

**Example**

.. literalinclude:: ../code-samples/plugins/push/mail.GMail/example.yaml
   :language: YAML
