# pnp.plugins.udf.simple.Counter

Memories a counter value which is increased everytime you call the udf.

__Arguments__

- **init (Optional[int])**: The initialization value of the counter. Default is 0.

__Result__

Returns the current counter.

__Examples__

```yaml
udfs:
  # Defines the udf. name is the actual alias you can call in selector expressions.
  - name: counter
    plugin: pnp.plugins.udf.simple.Counter
    args:
      init: 1
tasks:
  - name: countme
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        repeat: "Hello World"  # Repeats 'Hello World'
        interval: 1s  # Every second
    push:
      - plugin: pnp.plugins.push.simple.Echo
        selector:
          data: "lambda data: data"
          count: "lambda data: counter()"  # Calls the udf

```
