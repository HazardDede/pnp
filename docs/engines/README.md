# Engines

1\.  [General remarks](#generalremarks)  
2\.  [pnp.engines.SequentialEngine](#pnp.engines.sequentialengine)  
3\.  [pnp.engines.ThreadEngine](#pnp.engines.threadengine)  
4\.  [pnp.engines.ProcessEngine](#pnp.engines.processengine)  
5\.  [pnp.engines.AsyncEngine (0.18.0+)](#pnp.engines.asyncengine0.18.0+)  

<a name="generalremarks"></a>

## 1\. General remarks

If you do not specify any engine the `ThreadEngine` is chosen by default accompanied by the `AdvancedRetryHandler`.
This keeps maximum backwards compatibility.

This will probably change in the near future in favor to the `AsyncEngine`.

<a name="pnp.engines.sequentialengine"></a>

## 2\. pnp.engines.SequentialEngine

By using the `Sequential` engine you can run your configs as scripts. Given the example below, the "script" will
end when it has finished counting to 3. Make sure to use the `NoRetryHandler` to actually end the runner when
the pull has finished instead of retrying the "failed" `pull`. You cn only run a single task not multiple.
When you want to run multiple task in a concurrent manner you have to use the `ThreadEngine`, `ProcessEngine` or `AsyncEngine`.

```yaml
# Simple sequential handler
# Counts from 1 to 3 and then terminates
engine: !engine
  type: pnp.engines.SequentialEngine
  retry_handler: !retry
    # Is the key to termination after counting has finished
    type: pnp.engines.NoRetryHandler
tasks:
  - name: sequential
    pull:
      plugin: pnp.plugins.pull.simple.Count
      args:
        interval: 1s
        from_cnt: 1
        to_cnt: 4
    push:
      - plugin: pnp.plugins.push.simple.Echo

```

<a name="pnp.engines.threadengine"></a>

## 3\. pnp.engines.ThreadEngine

```yaml
# Will use threads to accomplish concurrency
# Drawback: If a plugin does not stop gracefully the termination will hang...
engine: !engine
  type: pnp.engines.ThreadEngine
  queue_worker: 1
  retry_handler: !retry
    type: pnp.engines.SimpleRetryHandler
tasks:
  - name: threading
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        interval: 1s
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo

```

<a name="pnp.engines.processengine"></a>

## 4\. pnp.engines.ProcessEngine

```yaml
# Will use multiprocessing to accomplish concurrency
# Drawback: Some plugins might not work or need to be aware of
engine: !engine
  type: pnp.engines.ProcessEngine
  queue_worker: 1
  retry_handler: !retry
    type: pnp.engines.SimpleRetryHandler
tasks:
  - name: process
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        interval: 1s
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo

```

<a name="pnp.engines.asyncengine0.18.0+"></a>

## 5\. pnp.engines.AsyncEngine (0.18.0+)

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
