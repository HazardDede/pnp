# Engines

In version `0.22.0` I've decided to remove all engines except for the `Async` engine.
Due to some tests this engine is amazingly stable, has great performance and you do not need to think about synchronizing parallel tasks stuff so much.

This decision was basically driven from a maintenance view of perspective.
In the future I like to add some infrastructural code like an api to communicate with the engine.
And I will not be able to integrate necessary changes to all of the engines.

By default the `async` engine is used implicitly:

```yaml
tasks:  # Implicit use of the AsyncEngine
  - name: async
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        interval: 1s
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo
```


You can add it explicitly. This might be useful in the future IF I decide to add variants of the `Async` engine.

```yaml
engine: !engine  # Use the AsyncEngine explicitly
  type: pnp.engines.AsyncEngine
  retry_handler: !retry
    type: pnp.engines.SimpleRetryHandler
tasks:
  - name: async
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        interval: 1s
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo

```
