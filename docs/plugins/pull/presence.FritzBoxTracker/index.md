# pnp.plugins.pull.net.PortProbe

Periodically asks a Fritz!Box router for the devices that were connected in the past or right now.

__Arguments__

- **host (str, optional)**: The IP address of your Fritz!Box. Default is 169.254.1.1</br>
- **user (str, optional)**: The user to use. Default is admin.<br/>
- **password (str, optional)**: The password to use. Default is an empty string.

Hint: By using the default values you should be able to connect to your Fritz!Box, because the necessary operation
can be performed anonymously.

__Result__

```yaml
{
    "ip": "192.168.178.2",
    "mac": "00:0a:95:9d:68:16",
    "status": "active",
    "name": "pc1"
}
```

__Examples__

```yaml
- name: fritzbox_tracker
  pull:
    plugin: pnp.plugins.pull.presence.FritzBoxTracker
    args:
      host: 169.254.1.1  # IP of your Fritz!Box. Default is 169.254.1.1
      user: ''  # User name. Default is admin
      password: admin  # Password. Default is an empty string
      instant_run: true  # ... and run as soon as pnp starts
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
