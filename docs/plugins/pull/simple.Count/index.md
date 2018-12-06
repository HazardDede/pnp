# pnp.plugins.pull.simple.Count

Emits every `wait` seconds a counting value which runs from `from_cnt` to `to_cnt`.
If `to_cnt` is None the counter will count to infinity.

__Arguments__

**wait (int)**: Wait the amount of seconds before emitting the next counter.<br/>
**from_cnt (int)**: Starting value of the counter.<br/>
**to_cnt (int, optional)**: End value of the counter. If not passed set to "infinity" (precise: int.max).

__Result__

Counter value (int).

__Examples__

```yaml
- name: count
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 1
      from_cnt: 1
      to_cnt: 10
  push:
    plugin: pnp.plugins.push.simple.Echo
```
