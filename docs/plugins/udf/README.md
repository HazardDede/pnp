# UDFs (User defined function)

## pnp.plugins.udf.hass.State

Fetches the state of an entity from home assistant by a rest-api request.

__Arguments__

- **url (str)**: The url to your home assistant instance (e.g. http://hass:8123)
- **token (str)**: The love live access token to get access to home assistant
- **timeout (Optional[int])**: Tell the request to stop waiting for a reponse after given number of seconds. Default is 5 seconds.

__Call Arguments__

- **entity_id (str)**: The entity to fetch the state<br>
- **attribute (Optional[str])**: Optionally you can fetch the state of one of the entities attributes.
Default is None (which means to fetch the state of the entity)

__Result__

Returns the current state of the entity or one of it's attributes. If the entity is not known to home assistant an exception is raised.
In case of an attribute does not exists, None will be returned instead to signal it's absence.

__Examples__

```yaml
udfs:
  # Defines the udf. name is the actual alias you can call in selector expressions.
  - name: hass_state
    plugin: pnp.plugins.udf.hass.State
    args:
      url: http://localhost:8123
      token: "{{env::HA_TOKEN}}"
tasks:
  - name: hass_state
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        repeat: "Hello World"  # Repeats 'Hello World'
        interval: 1s  # Every second
    push:
      - plugin: pnp.plugins.push.simple.Echo
        # Will only print the data when attribute azimuth of the sun component is above 200
        selector: "'azimuth is greater than 200' if hass_state('sun.sun', attribute='azimuth') > 200.0 else SUPPRESS"
      - plugin: pnp.plugins.push.simple.Echo
        # Will only print the data when the state of the sun component is above 'above_horizon'
        selector: "'above_horizon' if hass_state('sun.sun') == 'above_horizon' else SUPPRESS"

```
## pnp.plugins.udf.simple.Counter

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
## pnp.plugins.udf.simple.FormatSize

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
## pnp.plugins.udf.simple.Memory

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
