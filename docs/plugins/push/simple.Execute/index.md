# pnp.plugins.push.simple.Execute

Executes a command with given arguments in a shell of the operating system.
Both `command` and `args` may include placeholders (e.g. `{{placeholder}}`) which are injected at runtime
by passing the specified payload after selector transformation. Please see the Examples section for further details.

Will return the exit code of the command and optionally the output from stdout and stderr.

__Arguments__

- **command (str)**: The command to execute. May contain placeholders.
- **args (str or iterable, optional)**: The arguments to pass to the command. Default is no arguments.
May contain placeholders.
- **cwd (str, optional)**: Specifies where to execute the command (working directory).
Default is the folder where the invoked pnp-configuration is located.
- **timeout (duration literal, optional)**: Specifies how long the worker should wait for the command to finish.</br>
- **capture (bool, optional)**: If True stdout and stderr output is captured, otherwise not.

__Result__

Returns a dictionary that contains the `return_code` and optionally the output from `stdout` and `stderr` whether
`capture` is set or not. The output is a list of lines.

```yaml
{
    'return_code': 0
    'stdout': ["hello", "dude!"]
    'stderr': []
}
```

__Examples__

```yaml
- name: execute
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 1s
      from_cnt: 1
  push:
    plugin: pnp.plugins.push.simple.Execute
    selector:
      command: echo
      count: "lambda data: str(data)"
      labels:
        prefix: "The actual count is"
        iter: iterations
    args:
      command: "{{command}}"  # The command to execute (passed by selector)
      args:
        - "{{labels.prefix}}"
        - "{{count}}"  # The named argument passed at runtime by selector
        - "{{labels.iter}}"
      timeout: 2s
      cwd:  # None -> pnp-configuration directory
      capture: true  # Capture stdout and stderr
    deps:
      - plugin: pnp.plugins.push.simple.Echo

```

```yaml
- name: execute
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 1s
      from_cnt: 1
  push:
    plugin: pnp.plugins.push.simple.Execute
    selector:
      command: echo
      salutation: "\"hello you\""
    args:
      command: "{{command}}"  # The command to execute (passed by selector)
      args:
        - "{{salutation}}"
      timeout: 2s
      cwd:  # None -> pnp-configuration directory
      capture: true  # Capture stdout and stderr
    deps:
      - plugin: pnp.plugins.push.simple.Echo

```
