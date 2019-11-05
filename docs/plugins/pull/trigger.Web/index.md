# pnp.plugins.pull.trigger.Web

Wraps a poll-based pull and provides a rest-endpoint to externally trigger the poll action.
This will disable the cron-like / scheduling features of the polling component and simply
provides you an interface to call the component anytime you see fit.

__Arguments__

- **poll (Polling component)**: The polling component that you want to trigger externally. See example for configuration.
- **port (int)**: The port for the server to listen on.
- **endpoint (str, optional)**: The name of the endpoint. Default is `/trigger`.

Assume you set `port = 8080` and `endpoint = trigger` then your corresponding `curl` command
to trigger the polling externally would look like this:

```bash
curl http://localhost:8080/trigger
```

In case of success you get back a `200`. In case of error it's a `500`.

__Result__

The component will simply forward the result of the underlying component to dependent pushes.

__Examples__

```yaml
engine: !engine
  type: pnp.engines.AsyncEngine
  retry_handler: !retry
    type: pnp.engines.NoRetryHandler
tasks:
  - name: trigger_web
    pull:
      plugin: pnp.plugins.pull.trigger.Web
      args:
        port: 8080
        endpoint: '/'
        poll:
          plugin: pnp.plugins.pull.monitor.Stats
    push:
      plugin: pnp.plugins.push.simple.Echo

```

Test it out:

```bash
curl http://localhost:8080/
```

```yaml
- name: trigger_web
  pull:
    plugin: pnp.plugins.pull.trigger.Web
    args:
      port: 8080
      poll:
        plugin: pnp.plugins.pull.traffic.DeutscheBahn
        args:
          origin: Hamburg Hbf
          destination: München Hbf
          only_direct: true  # Only show direct transfers wo change. Default is False.
  push:
    plugin: pnp.plugins.push.simple.Echo

```

Test it out:

```bash
curl http://localhost:8080/trigger
```
