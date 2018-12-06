# pnp.plugins.pull.monitor.Stats

Emits every `interval` various metrics / statistics about the host system. Please see the 'Result' section for available metrics.

__Result__

```yaml
{
	'cpu_count': 4,
	'cpu_freq': 700,  # in Mhz
	'cpu_use': 6.6,  # in %
	'cpu_temp': 52.6,  # in °C (might not be available on all systems, e.g. MacOS)
	'memory_use': 56.0,  # in %
	'swap_use': 23.2,  # in %
	'disk_use': 69.8,  # in %  (of your root)
	'load_1m': 1.81591796875,  # CPU queue length last minute
	'load_5m': 2.06689453125,  # CPU queue length last 5 minutes
	'load_15m': 2.15478515625  # CPU queue length last 15 minutes
}
```

__Examples__

```yaml
- name: stats
  pull:
    plugin: pnp.plugins.pull.monitor.Stats
    args:
      interval: 10s
      instant_run: True
  push:
    plugin: pnp.plugins.push.simple.Echo
```
