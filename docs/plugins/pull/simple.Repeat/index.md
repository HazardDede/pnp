# pnp.plugins.pull.simple.Repeat

Emits every `interval` seconds the same `repeat`.

__Arguments__

- **interval (duration literal)**: Wait the amount of seconds before emitting the next `repeat`.
- **wait (int)**: DEPRECATED! Use `interval` instead.
- **repeat (any)**: The object to emit.

__Result__

Emits the `repeat`-object as it is.

__Examples__

```yaml
- name: repeat
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      repeat: "Hello World"  # Repeats 'Hello World'
      interval: 1s  # Every second
  push:
    plugin: pnp.plugins.push.simple.Echo

```
