# pnp.plugins.pull.simple.Count

Emits every `interval` seconds a counting value which runs from `from_cnt` to `to_cnt`.
If `to_cnt` is None the counter will count to infinity (or more precise to sys.maxsize).

__Arguments__

- **interval (duration literal)**: Wait the amount of seconds before emitting the next counter.
- **wait (int)**: DEPRECATED! Use `interval` instead.
- **from_cnt (int)**: Starting value of the counter.
- **to_cnt (int, optional)**: End value of the counter. If not passed set to "infinity" (precise: int.max).

__Result__

Counter value (int).

__Examples__

```yaml
- name: count
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 1s
      from_cnt: 1
      to_cnt: 10
  push:
    plugin: pnp.plugins.push.simple.Echo

```
