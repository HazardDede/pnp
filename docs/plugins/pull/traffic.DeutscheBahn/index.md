# pnp.plugins.pull.traffic.DeutscheBahn

Polls the Deutsche Bahn website using the `schiene` package to find the next trains scheduled
for a given destination from a specific origin station.


__Arguments__

- **origin (str)**: The origin station.
- **destination (str)**: The destination station.
- **only_direct (bool, optional)**: If set to True only show direct connections (without transfer). Default is False.

__Result__

```yaml
[{
	"departure": "09:01",
	"arrival": "15:09",
	"travel_time": "6:05",
	"products": ["ICE"],
	"transfers": 1,
	"canceled": false,
	"delayed": true,
	"delay_departure": 3,
	"delay_arrival": 0
}, {
	"departure": "09:28",
	"arrival": "15:39",
	"travel_time": "6:11",
	"products": ["ICE"],
	"transfers": 0,
	"canceled": false,
	"delayed": false,
	"delay_departure": 0,
	"delay_arrival": 0
}, {
	"departure": "09:36",
	"arrival": "16:02",
	"travel_time": "6:26",
	"products": ["ICE"],
	"transfers": 1,
	"canceled": false,
	"delayed": false,
	"delay_departure": 0,
	"delay_arrival": 0
}]
```

__Examples__

```yaml
- name: deutschebahn
  pull:
    plugin: pnp.plugins.pull.traffic.DeutscheBahn
    args:
      origin: Hamburg Hbf
      destination: München Hbf
      only_direct: true  # Only show direct transfers wo change. Default is False.
      instant_run: true
      interval: 1m
  push:
    plugin: pnp.plugins.push.simple.Echo

```
