# pnp.plugins.pull.ZwayReceiver

Setups a http server to process incoming GET-requests from the Zway-App [`HttpGet`](https://github.com/hplato/Zway-HTTPGet/blob/master/index.js).

__Arguments__

**url_format (str)**: The url_format that is configured in your HttpGet App. If you configured
`http://<ip>:<port>/set?device=%DEVICE%&state=%VALUE%` (default of the App), you basically have to copy the path
component `set?device=%DEVICE%&state=%VALUE%` to be your `url_format`.<br/>
**device_mapping (Or(Dict[Str, Str], Dict[Str, Dict]), optional)**: A mapping to map the somewhat cryptic virtual device names to
human readable ones. Default is None, which means that no mapping will be performed. Two ways possible:
1. Ordinary mapping from virtual device name -> alias.
2. Enhanced mapping from virtual device name to dictionary with additional properties. One property has to be alias.<br/>
**ignore_unknown_devices (bool, optional)**: If set to True all incoming requests that are associated with an device
that is not part of the mapping will be ignored. Default is False.<br/>

Additionally the component will accept any arguments that `pnp.plugins.pull.http.Server` would accept.

__Result__

Given the url_format `%DEVICE%?value=%VALUE%`, the url `http://<ip>:<port>/set?vdevice1?value=5.5` and
the device_mapping `vdevice1 -> alias of vdevice1` the emitted message will look like this:

```yaml
{
    'device_name': 'alias of vdevice1',
    'raw_device': 'vdevice1'
    'value': 5.5,
    'props': {}
}
```

__Examples__

```yaml
- name: zway_receiver
  pull:
    plugin: pnp.plugins.pull.zway.ZwayReceiver
    args:
      port: 5000
      device_mapping:
        vdevice1:  # Props = {type: motion}
          alias: dev1
          type: motion
        vdevice2:  # Props = {type: switch, other_prop: foo}
          alias: dev2
          type: switch
          other_prop: foo
        vdevice3: dev3  # props == {}
      url_format: "%DEVICE%?value=%VALUE%"
      ignore_unknown_devices: False
  push:
    - plugin: pnp.plugins.push.simple.Echo
      selector: "'Got value {} from device {} ({}) with props {}'.format(data.value, data.device_name, data.raw_device, data.props)"
```
