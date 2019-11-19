# pnp.plugins.push.simple.Wait

Performs a sleep operation and waits for some time to pass by.

IMPORTANT: Some engines do have a worker pool (like the `ThreadEngine`).
This push will use a slot in this pool and will only release it when the waiting
interval is over. Use with caution.
It is safe to use with the `AsyncEngine`.

__Arguments__

- **wait_for (str or int or float)**: The time to wait for before proceeding. You can pass
literals such as 5s, 1m; ints such as 1, 2, 3 or floats such as 0.5. In the end everything
will be converted to it's float representation (1 => 1.0; 5s => 5.0; 1m => 60.0; 0.5 => 0.5)

__Result__

Will return the payload as it is for easy chaining of dependencies (see example).

__Examples__

```yaml
engine: !engine  # Practically only safe to use with the AsyncEngine
  type: pnp.engines.AsyncEngine
  retry_handler: !retry
    type: pnp.engines.NoRetryHandler
tasks:
  - name: wait
    pull:
      plugin: pnp.plugins.pull.simple.Count  # Let's count
      args:
        interval: 1s
    push:
      - plugin: pnp.plugins.push.simple.Echo
        selector: "'START WAITING: {}'.format(payload)"
        deps:
          - plugin: pnp.plugins.push.simple.Wait
            args:
              wait_for: 3s
            deps:
              - plugin: pnp.plugins.push.simple.Echo
                selector: "'END WAITING: {}'.format(payload)"

```
