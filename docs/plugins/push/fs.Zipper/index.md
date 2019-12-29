# pnp.plugins.push.fs.Zipper

The push expects a directory or a file path to be passed as the payload.
As long it's a valid path it will zip the directory or the single file and return
the absolute path to the created zip file.

Hint: You can use a so called .zipignore file to exclude files and directories from zipping.
It works - mostly - like a .gitignore file.

__Arguments__

- **source (str, optional)**: Specifies the source directory or file to zip. If not passed the source can be specified by the envelope at runtime.
- **out_path (str, optional)**: Specifies the path to the general output path where all target zip files should be generated. If not passed the systems temp directory is used.

__Result__

Will return an absolute path to the zip file created.

__Examples__

```yaml
- name: zipper
  pull:
    plugin: pnp.plugins.pull.simple.Cron
    args:
      expressions:
        - "*/1 * * * * /path/to/backup"
  push:
    plugin: pnp.plugins.push.fs.Zipper
    args:
      out_dir: "{{env::BACKUP_DIR}}"
    deps:
      plugin: pnp.plugins.push.simple.Echo

```
