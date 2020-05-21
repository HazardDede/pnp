# pnp.plugins.pull.zway.ZwayReceiver

Setup a route /zway on the builtin api server to process incoming GET requests from the Zway app [`HttpGet`](https://github.com/hplato/Zway-HTTPGet/blob/master/index.js)

Remarks:
* You have to configure your HttpGET app with the `URL to get` set to `http://<host>:<port>/zway?device=%DEVICE%&value=%value%`
* You need to enable the api via configuration to make this work.

__Arguments__

- **mode ([mapping, auto, both])**: If set to `mapping` (default) you should provide the `device_mapping` to manually map your virtual devices.
If set to `auto` the plugin will try to determine the device_id, command class, mode and the type on it's own. If set to `both` the plugin
will first try the `device_mapping` and then perform the auto-magic.</br>
- **device_mapping (Or(Dict[Str, Str], Dict[Str, Dict]), optional)**: A mapping to map the somewhat cryptic virtual device names to
human readable ones. Default is None, which means that no mapping will be performed. Two ways possible:
1. Ordinary mapping from virtual device name -> alias.
2. Enhanced mapping from virtual device name to dictionary with additional properties. One property has to be alias.
- **ignore_unknown_devices (bool, optional)**: If set to True all incoming requests that are associated with an device
that is not part of the mapping or - when mode = [auto, both] - cannot be auto mapped will be ignored. Default is False.

__Result__


Issuing `curl -X GET "http://<ip>:<port>/zway?device=vdevice1&value=5.5"` and the device_mapping `vdevice1 -> alias of vdevice1` the emitted message will look like this:

```json
{
    "device_name": "alias of vdevice1",
    "raw_device": "vdevice1"
    "value": "5.5",
    "props": {}
}
```

When `mode` is `auto` or `both` the plugin will try to determine the device id and the type of the virtual device on it's
own. Given the virtual device name `ZWayVDev_zway_7-0-48-1` and the value of `on` will produce the following:

```json
{
    "device_name": "7",
    "raw_device": "ZWayVDev_zway_7-0-48-1",
    "value": "on"
    "props": {
        "command_class": "48",
        "mode": "1",
        "type": "motion"
    }
}
```

__Examples__

```yaml
#
# Registers the /zway endpoint to the builtin api server.
#
# Use the manual mapping of device names
#   curl -X GET "http://localhost:9999/zway?device=vdevice1&value=on"
#
# Use the automapper:
#   curl -X GET "http://localhost:9999/zway?device=ZWayVDev_zway_21-0-49-1&value=21.2"
#
# Unknown device (no manual mapping and no automapping possible)
#   curl -X GET "http://localhost:9999/zway?device=unknown&value=off"
#

api:  # You need to enable the api
  port: 9999
tasks:
  - name: zway_receiver
    pull:
      plugin: pnp.plugins.pull.zway.ZwayReceiver
      args:
        mode: both  # mapping, auto or both
        device_mapping:
          vdevice1:  # Props = {type: motion}
            alias: dev1
            type: motion
          vdevice2:  # Props = {type: switch, other_prop: foo}
            alias: dev2
            type: switch
            other_prop: foo
          vdevice3: dev3  # props == {}
        ignore_unknown_devices: false
    push:
      - plugin: pnp.plugins.push.simple.Echo
        selector: "'Received value `{}` from device `{}` ({}) with props {}'.format(data.value, data.device_name, data.raw_device, data.props)"

```
