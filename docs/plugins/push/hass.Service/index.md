# pnp.plugins.push.hass.Service

Calls a home assistant service providing the payload as service-data.

__Arguments__

- **url (str)**: The url to your home assistant instance (e.g. http://hass:8123)
- **token (str)**: The love live access token to get access to home assistant
- **domain (str)**: The domain the service.
- **service (str)**: The name of the service.
- **timeout (Optional[int])**: Tell the request to stop waiting for a reponse after given number of seconds. Default is 5 seconds.

__Result__

Returns the payload as-is for better chaining (this plugin can't add any useful information).

__Examples__

```yaml
# Calls the frontend.set_theme service to oscillate between a "light" and a "dark" theme
- name: hass_service
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 10s
  push:
    plugin: pnp.plugins.push.hass.Service
    selector:
      name: "lambda i: 'clear' if i % 2 == 0 else 'dark'"
    args:
      url: http://localhost:8123
      token: "{{env::HA_TOKEN}}"
      domain: frontend
      service: set_theme

```

```yaml
# Calls the notify.pushbullet service to send a message with the actual counter
- name: hass_service
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 10s
  push:
    plugin: pnp.plugins.push.hass.Service
    selector:
      message: "lambda i: 'Counter: ' + str(i)"
    args:
      url: http://localhost:8123
      token: "{{env::HA_TOKEN}}"
      domain: notify
      service: pushbullet

```
