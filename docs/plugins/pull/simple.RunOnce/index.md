# pnp.plugins.pull.simple.RunOnce

Takes another valid `plugins.pull.Polling` component and immediately executes it and ventures
down the given `plugins.push` components. If no component to wrap is given it will simple execute the
push chain.

__Arguments__

- **poll (Polling component, optional)**: The polling component you want to run once. If not passed the push chain
    will be executed.

__Result__

Emits the payload of the polling component if given. Otherwise an empty dictionary will be returned.

__Examples__

```yaml
- name: run_once
  pull:
    plugin: pnp.plugins.pull.simple.RunOnce
  push:
    plugin: pnp.plugins.push.simple.Echo

```

```yaml
- name: run_once_wrapped
  pull:
    plugin: pnp.plugins.pull.simple.RunOnce
    args:
      poll:
        plugin: pnp.plugins.pull.monitor.Stats
  push:
    plugin: pnp.plugins.push.simple.Echo

```
