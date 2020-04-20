# Engines

1\.  [General](#general)  
2\.  [pnp.engines.AsyncEngine (0.18.0+)](#pnp.engines.asyncengine0.18.0+)  

<a name="general"></a>

## 1\. General

In version `0.22.0` I've decided to remove all engines except for the `AsyncEngine`. Due to some tests this engine
is amazingly stable, has great performance and you do not need to think about synchronizing parallel tasks stuff so much.

This decision was basically driven from a maintenance view of perspective. In the future I like to add some
infrastructural code like an api to communicate with the engine. And I will not be able to integrate necessary changes
to all of the engines.


<a name="pnp.engines.asyncengine0.18.0+"></a>

## 2\. pnp.engines.AsyncEngine (0.18.0+)

```yaml
# Will use asyncio to accomplish concurrency

engine: !engine
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
