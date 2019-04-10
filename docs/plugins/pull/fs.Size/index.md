# pnp.plugins.pull.fs.Size

Periodically determines the size of the specified files or directories in bytes.

__Arguments__

- **paths (List of files/directories)**: List of files and/or directories to monitor their sizes in bytes.
- **fail_on_error (bool, optional)**: If set to true, the plugin will raise an error when a
    file/directory does not exists or any other file system related error occurs. Otherwise the plugin
    will proceed and simply report None as the file size. Set to True by default.

Hint: Be careful when adding directories with a large amount of files. This will be prettly slow cause
the plugin will iterate over each file and determine it's individual size.

__Result__

Example of an emitted message. Size is in bytes.

```yaml
{
  "logs": 32899586,
  "copy": 28912
}
```

__Examples__

```yaml
- name: file_size
  pull:
    plugin: pnp.plugins.pull.fs.Size
    args:
      instant_run: true
      interval: 5s
      fail_on_error: false
      paths:
        logs: /var/log  # directory - recursively determines size
        copy: /bin/cp  # file
  push:
    plugin: pnp.plugins.push.simple.Echo

```
