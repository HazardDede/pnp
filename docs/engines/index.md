If you do not specify any engine the `ThreadEngine` is chosen by default accompanied by the `AdvancedRetryHandler`.
This keeps maximum backwards compatibility.

# pnp.engines.sequential.SequentialEngine

By using the `Sequential` engine you can run your configs as scripts. Given the example below, the "script" will
end when it has finished counting to 3. Make sure to use the `NoRetryHandler` to actually end the runner when
the pull has finished instead of retrying the "failed" `pull`. You cn only run a single task not multiple.
When you want to run multiple task in a concurrent manner you have to use the `ThreadEngine` or the `ProcessEngine`.

```yaml
# Simple sequential handler
# Counts from 1 to 3 and then terminates
engine: !engine
  type: pnp.engines.sequential.SequentialEngine
  retry_handler: !retry
    type: pnp.engines.NoRetryHandler  # Is the key to termination after counting has finished
tasks:
  - name: sequential
    pull:
      plugin: pnp.plugins.pull.simple.Count
      args:
        wait: 1
        from_cnt: 1
        to_cnt: 4
    push:
      - plugin: pnp.plugins.push.simple.Echo

```

# pnp.engines.thread.ThreadEngine

```yaml
# Will use threads to accomplish concurrency
# Drawback: If a plugin does not stop gracefully the termination will hang...
engine: !engine
  type: pnp.engines.thread.ThreadEngine
  queue_worker: 1
  retry_handler: !retry
    type: pnp.engines.SimpleRetryHandler
tasks:
  - name: threading
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        wait: 1
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo
```

# pnp.engines.process.ProcessEngine

```yaml
# Will use multiprocessing to accomplish concurrency
# Drawback: Some plugins might not work or need to be aware of
engine: !engine
  type: pnp.engines.process.ProcessEngine
  queue_worker: 1
  retry_handler: !retry
    type: pnp.engines.SimpleRetryHandler
tasks:
  - name: process
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        wait: 1
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo
```
