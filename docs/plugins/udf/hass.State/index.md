# pnp.plugins.udf.hass.State

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
