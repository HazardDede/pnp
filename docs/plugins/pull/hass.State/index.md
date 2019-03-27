# pnp.plugins.pull.hass.State

Connects to the `home assistant` websocket api and listens for state changes. If no `include` or `exclude` is defined
it will report all state changes. If `include` is defined only entities that match one of the specified patterns will
be emitted. If `exclude` if defined entities that match at least one of the specified patterns will be ignored. `exclude`
patterns overrides `include` patterns.


__Arguments__

- **host (str)**: Url to your `home assistant` instance (e.g. http://my-hass:8123)
- **token (str)**: Your long lived access token to access the websocket api. See below for further instructions
- **include (str or list[str])**: Patterns of entity state changes to include. All state changes that do not match the
defined patterns will be ignored</br>
- **exclude (str or list[str]**:Patterns of entity state changes to exclude. All state changes that do match the defined
patterns will be ignored

Hints:
* `include` and `exclude` support wildcards (e.g `*` and `?`)
* `exclude` overrides `include`. So you can `include` everything from a domain (`sensor.*`) but exclude individual entities.
* Create a long lived access token: [Home Assistant documentation](https://developers.home-assistant.io/docs/en/auth_api.html#long-lived-access-token)

__Result__

The emitted result always contains the `entity_id`, `new_state` and `old_state`:

```yaml
{
  'entity_id': 'light.bedroom_lamp',
  'old_state': {
    'state': 'off',
    'attributes': {},
    'last_changed': '2019-01-08T18:24:42.087195+00:00',
    'last_updated': '2019-01-08T18:40:40.011459+00:00'
  },
  'new_state': {
    'state': 'on',
    'attributes': {},
    'last_changed': '2019-01-08T18:41:06.329699+00:00',
    'last_updated': '2019-01-08T18:41:06.329699+00:00'
  }
}
```

__Examples__

```yaml
- name: hass_state
  pull:
    plugin: pnp.plugins.pull.hass.State
    args:
      url: http://localhost:8123
      token: "{{env::HA_TOKEN}}"
      exclude:
        - light.lamp
      include:
        - light.*
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
