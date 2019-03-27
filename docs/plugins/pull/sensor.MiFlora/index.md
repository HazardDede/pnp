# pnp.plugins.pull.sensor.MiFlora

Periodically polls a `xiaomi miflora plant sensor` for sensor readings (temperature, conductivity, light, ...) via btle.

Requires extra `miflora`.

__Arguments__

- **mac (str)**: The device to poll identified by mac address. See below for further instructions.
- **adapter (str, optional)**: The bluetooth adapter to use (if you have more than one). Default is 'hci0' which is
 your default bluetooth device.

Start a bluetooth scan to determine the MAC addresses of the sensor (look for Flower care or Flower mate entries)
using this command:

```bash
$ sudo hcitool lescan
LE Scan ...
F8:04:33:AF:AB:A2 [TV] UE48JU6580
C4:D3:8C:12:4C:57 Flower mate
[...]
```

__Result__

Emits a dictionary that contains an entry for every sensor of the plant sensor device:

```yaml
{
  "conductivity": 800,
  "light": 2000,
  "moisture": 42,
  "battery": 72,
  "temperature": 24.2,
  "firmaware": "3.1.9"
}
```

__Examples__

```yaml
- name: miflora
  pull:
    plugin: pnp.plugins.pull.sensor.MiFlora
    args:
      mac: 'C4:7C:8D:67:50:AB'  # The mac of your miflora device
      instant_run: true
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
