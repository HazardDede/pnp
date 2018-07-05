# pnp.plugins.pull.simple.Repeat

Emits every `wait` seconds the same `repeat`.

__Arguments__

**wait (int)**: Wait the amount of seconds before emitting the next repeat.<br/>
**repeat (any)**: The object to emit.

__Result__

Emits the `repeat`-object as it is.

__Examples__

```yaml
- name: repeat
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      repeat: "Hello World"  # Repeats 'Hello World'
      wait: 1  # Every second
  push:
    plugin: pnp.plugins.push.simple.Echo
```
