notify.Slack
^^^^^^^^^^^^

=================================== ====== ============ ========
plugin                              type   extra        version
=================================== ====== ============ ========
pnp.plugins.push.notify.Slack       push   none         0.20.0
=================================== ====== ============ ========

**Description**

Sends a message to a given `Slack <http://www.slack.com>`_ channel.

You can specify the channel, the name of the poster, the icon of the poster
and a list of users to ping.

**Arguments**

+------------+-----------+------+-----------+-----+----------------------------------------------------------------------------------+
| name       | type      | opt. | default   | env | description                                                                      |
+============+===========+======+===========+=====+==================================================================================+
| api_key    | str       | no   | n/a       | no  | The api key of your slack oauth token.                                           |
+------------+-----------+------+-----------+-----+----------------------------------------------------------------------------------+
| channel    | str       | no   | n/a       | yes | The channel to post the message to.                                              |
+------------+-----------+------+-----------+-----+----------------------------------------------------------------------------------+
| username   | str       | yes  | PnP       | yes | The username of the message poster.                                              |
+------------+-----------+------+-----------+-----+----------------------------------------------------------------------------------+
| emoji      | str       | yes  | `:robot:` | yes | The emoji of the message poster.                                                 |
+------------+-----------+------+-----------+-----+----------------------------------------------------------------------------------+
| ping_users | List[str] | yes  | None      | yes | A list of users to ping when the message is posted. By default no one is ping'd. |
+------------+-----------+------+-----------+-----+----------------------------------------------------------------------------------+

**Result**

Will return the payload as it is for easy chaining of dependencies.

**Example**

.. literalinclude:: ../code-samples/plugins/push/notify.Slack/example.yaml
   :language: YAML
