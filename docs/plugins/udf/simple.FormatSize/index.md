# pnp.plugins.udf.simple.FormatSize

Returns the size of a file (or whatever) as a human readable size (e.g. bytes, KB, MB, GB, TB, PB).
The input is expected to be at byte scale.

__Arguments__

- **size_in_bytes (float|int)**: The size in bytes to format to a human readable format.

__Result__

Returns the argument in a human readable size format.

__Examples__

```yaml
udfs:
  # Defines the udf. name is the actual alias you can call in selector expressions.
  - name: fsize
    plugin: pnp.plugins.udf.simple.FormatSize
    args:
      init: 1
tasks:
  - name: format_size
    pull:
      plugin: pnp.plugins.pull.fs.Size
      args:
        instant_run: true
        interval: 5s
        fail_on_error: false
        paths:
          logs: /var/log  # directory - recursively determines size
          copy: /bin/cp  # file
    push:
      plugin: pnp.plugins.push.simple.Nop
      selector: "[(k ,v) for k, v in data.items()]"  # Transform the dictionary into a list
      deps:
        plugin: pnp.plugins.push.simple.Echo
        unwrap: true  # Call the push for each individual item in the list
        selector:
          object: "lambda d: d[0]"
          data: "lambda d: fsize(d[1])"

```
