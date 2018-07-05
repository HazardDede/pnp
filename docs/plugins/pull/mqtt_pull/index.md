# pnp.plugins.pull.mqtt.MQTTPull

Pulls messages from the specified topic from the given mosquitto mqtt broker (identified by host and port).

__Arguments__

**host (str)**: Host where the mosquitto broker is running.<br/>
**port (int)**: Port where the mosquitto broker is listening.<br/>
**topic (str)**: Topic to pull messages from.
    You can listen to multiple topics by using the #-wildcard (e.g. `test/#` will listen to all topics underneath test).

All arguments can be automatically injected via environment variables with `MQTT` prefix (e.g. MQTT_HOST).

__Result__

The emitted message will look like this:
```yaml
{
    'topic': 'test/device/device1',
    'levels': ['test', 'device', 'device1']
    'payload': 'The actual event message'
}
```

__Examples__

```yaml
- name: mqtt
  pull:
    plugin: pnp.plugins.pull.mqtt.MQTTPull
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    plugin: pnp.plugins.push.simple.Echo
```

