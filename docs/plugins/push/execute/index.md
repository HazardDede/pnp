# pnp.plugins.push.simple.Execute

Executes a command with given arguments in a shell of the operating system.

Will return the exit code of the command and optionally the output from stdout and stderr.

__Arguments__

**command (str)**: The command to execute.<br/>
**args (str or iterable, optional)**: The arguments to pass to the command. Default is no arguments.<br/>
**cwd (str, optional)**: Specifies where to execute the command (working directory). Default is current working directory.<br/>
**timeout (duration literal, optional)**: Specifies how long the worker should wait for the command to finish.</br>
**capture (bool, optional)**: If True stdout and stderr output is captured, otherwise not.

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
      wait: 1
      from_cnt: 1
      to_cnt: 10
  push:
    plugin: pnp.plugins.push.simple.Execute
    args:
      command: date  # The command to execute
      args:  # Argument passed to the command
        - "-v"
        - "-1d"
        - "+%Y-%m-%d"
      timeout: 2s
      cwd:  # None -> current directory
      capture: True  # Capture stdout and stderr
    deps:
      - plugin: pnp.plugins.push.simple.Echo
```
