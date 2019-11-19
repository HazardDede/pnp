# pnp.plugins.push.mqtt.Publish

Will push the given `payload` to a mqtt broker (in this case mosquitto).
The broker is specified by `host` and `port`. In addition a topic needs to be specified were the payload
is pushed to (e.g. home/living/thermostat).

The `payload` will be pushed as it is. No transformation is applied. If you need to some transformations, use the
selector.

__Arguments__

- **host (str)**: The host where the mosquitto broker is running.
- **port (int, optional)**: The port where the mosquitto broker is listening. Default is 1883.
- **topic (str, optional)**: The topic to subscribe to. If set to None the envelope of the
    payload has to contain a 'topic' key or the push will fail (default is None). If both exists
    the topic from the envelope will overrule the __init__ one.
- **retain (bool, optional)**: If set to True will mark the message as retained. Default is False.
    See the mosquitto man page for further guidance
    [https://mosquitto.org/man/mqtt-7.html](https://mosquitto.org/man/mqtt-7.html).
- **multi (bool, optional)**: If set to True the payload is expected to be a dictionary. Each item of that dictionary will
be send individually to the broker. The key of the item will be appended to the configured topic. The value of the item
is the actual payload. Default is False.

__Result__

For chaining of pushes the payload is simply returned as is.

__Examples__

```yaml
- name: mqtt
  pull:
    plugin: pnp.plugins.pull.simple.Count
  push:
    # Will push the counter to the 'home/counter/state' topic
    plugin: pnp.plugins.push.mqtt.Publish
    args:
      host: localhost
      topic: home/counter/state
      port: 1883
      retain: true

```

```yaml
- name: mqtt
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 1s
  push:
    plugin: pnp.plugins.push.mqtt.Publish
    # Lets override the topic via envelope mechanism
    # Will publish even counts on topic 'even' and uneven counts on 'uneven'
    selector:
      data: "lambda data: data"
      topic: "lambda data: 'test/even' if int(data) % 2 == 0 else 'test/uneven'"
    args:
      host: localhost
      port: 1883

```

```yaml
- name: mqtt
  pull:
    # Periodically gets metrics about your system
    plugin: pnp.plugins.pull.monitor.Stats
    args:
      instant_run: true
      interval: 10s
  push:
    # Push them to the mqtt
    plugin: pnp.plugins.push.mqtt.Publish
    args:
      host: localhost
      topic: devices/localhost/
      port: 1883
      retain: true
      # Each item of the payload-dict (cpu_count, cpu_usage, ...) will be pushed to the broker as multiple items.
      # The key of the item will be appended to the topic, e.g. `devices/localhost/cpu_count`.
      # The value of the item is the actual payload.
      multi: true

```
