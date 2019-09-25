# pnp.plugins.pull.net.PortProbe

Periodically establishes socket connection to check if anybody is listening on a given
server on a specific port.

__Arguments__

- **port (int)**: The port to probe if something is listening.</br>
- **server (str, optional)**: Server name or ip address. Default is localhost.<br/>
- **timeout (float, optional)**: Timeout for remote operations. Default is 1.0.

__Result__

```yaml
{
    "server": "www.google.de",
    "port": 80,
    "reachable": True
}
```

__Examples__

```yaml
- name: port_probe
  pull:
    plugin: pnp.plugins.pull.net.PortProbe
    args:
      server: localhost  # Server name or ip address, default is localhost
      port: 9999  # The port to probe if somebody is listening
      interval: 5s  # Probe the port every five seconds ...
      instant_run: true  # ... and run as soon as pnp starts
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
