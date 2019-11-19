# pnp.plugins.udf.simple.Memory

Returns a previously memorized value when called.

__Arguments__

- **init (any, optional)**: The initial memory of the plugin. When not set initially the first call
will return the value of `new_memory`, if specified; otherwise `None`.

__Call Arguments__

- **new_memory (any, optional)**: After emitting the current memorized value the current memory is overwritten by this value.
Will only be overwritten if the parameter is specified.

__Result__

Returns the memorized value.

__Examples__

```yaml
udfs:
  - name: mem
    plugin: pnp.plugins.udf.simple.Memory
    args:
      init: 1
tasks:
  - name: countme
    pull:
      plugin: pnp.plugins.pull.simple.Count
      args:
        from_cnt: 1
        interval: 1s  # Every second
    push:
      - plugin: pnp.plugins.push.simple.Echo
        # Will memorize every uneven count
        selector: "mem() if data % 2 == 0 else mem(new_memory=data)"

```
