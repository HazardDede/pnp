# pnp.plugins.push.notify.Slack

Sends a message to a given [Slack](http://www.slack.com) channel.

You can specify the channel, the name of the poster, the icon of the poster
and a list of users to ping.

__Arguments__

- **api_key (str)**: The api key of your slack oauth token
- **channel (str)**: The channel to post the message to
- **username (str, optional)**: The username of the message poster. Defaults to PnP
- **emoji (str, optional)**: The emoji of the message poster. Defaults to :robot:
- **ping_users (List[str], optional)**: A list of users to ping when the message is posted. By default non one is ping'd.

You can override the `channel`, `username`, `emoji` and the `ping_users` list by the envelope. See the example for more details.

__Result__

Will return the payload as it is for easy chaining of dependencies.

__Examples__

```yaml
- name: slack
  pull:
    plugin: pnp.plugins.pull.simple.Count  # Let's count
    args:
      wait: 10
  push:
    - plugin: pnp.plugins.push.notify.Slack
      selector:
        data: "lambda data: 'This is the counter: {}'.format(data)"
        # You can override the channel if necessary
        # channel: "lambda data: 'test_even' if int(data) % 2 == 0 else 'test_odd'"
        # You can override the username if necessary
        # username: the_new_user
        # You can override the emoji if necessary
        # emoji: ':see_no_evil:'
        # You can override the ping users if necessary
        # ping_users:
        #   - clone_dede
      args:
        api_key: "{{env::SLACK_API_KEY}}"  # Your slack api key.
        channel: test  # The channel to post to. Mandatory. Overridable by envelope.
        username: slack_tester  # The username to show. Default is PnP. Overridable by envelope
        emoji: ':pig:'  # The emoji to use. Default is :robot: . Overridable by envelope
        ping_users:  # The users you want to ping when the message is send. Overridable by envelope
          - dede

```
