# pnp.plugins.pull.gpio.Watcher

Listens for low/high state changes on the configured gpio pins.

__Arguments__

**pins (list)**: The gpio pins to observe for state changes. Please see the examples section on how to configure it.<br/>
**default (on of [rising, falling, switch, motion]**: The default edge that is applied when not configured. Please see the examples section for further details.

__Result__

```yaml
{
    "gpio_pin": 17  # The gpio pin which state has changed
    "event": rising  # One of [rising, falling, switch, motion_on, motion_off]
}
```

__Examples__

```yaml
- name: gpio
  pull:
    plugin: pnp.plugins.pull.gpio.Watcher
    args:
      default: rising
      pins:
        - 2               # No mode specified: Default mode (in this case 'rising')
        - 2               # Duplicates will get ignored
        - 3:rising        # Equal to '3' (without explicit mode)
        - 3:falling       # Get the falling event for gpio pin 3 as well
        - 4:switch        # Uses some debouncing magic and emits only one rising event
        - 5:switch(1000)  # Specify debounce in millseconds (default is 500ms)
        - 5:switch(500)   # Duplicates - even when they have other arguments - will get ignored
        - 7:motion        # Uses some delay magic to emit only one motion on and one motion off event
        - 9:motion(1m)    # Specify delay (default is 30 seconds)
  push:
    - plugin: pnp.plugins.push.simple.Echo
```