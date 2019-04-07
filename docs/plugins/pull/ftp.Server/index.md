# pnp.plugins.pull.ftp.Server

Runs a ftp server on the specified port to receive and send files by ftp protocol.
Optionally sets up a simple user/password authentication mechanism.


Requires extra `ftp`.

__Arguments__

- **directory (Optional[str])**: The directory to serve via ftp protocol. If not given a directory is created is created temporarily to accept incoming uploads.
- **port (Optional[int]]**: The port to listen on. If not specified the ftpserver will listen on `2121`.
- **user_pwd (Optional[Or(str, tuple)]**: User/password combination (as a tuple/list; see example). You may specify the user only - password will be empty OR you can enable anonymous access by not providing the argument.
- **events (Optional[List])**: A list of events to subscribe to. Available events are: connect, disconnect, login, logout, file_received, file_sent, file_received_incomplete, file_sent_incomplete. By default all events are subscribed.
- **max_cons (Optional[int])**: The maximum number of simultaneous connections the ftpserver will permit. Default is 256.
- **max_cons_ip (Optional[int])**: The maximum number of simultaneous connections from the same ip. Default is 5.

__Result__

All emitted messages will have an event field to identify the type of the event and an - optional - data field.
The data field will contain the user for login/logout events and the file_path for file-related events.

```yaml
{
  "event": "file_received",
  "data": {
    "file_path": "/private/tmp/ftp/test.txt"
  }
}
```

__Examples__

```yaml
- name: ftp_server
  pull:
    plugin: pnp.plugins.pull.ftp.Server
    args:
      directory: "{{env::FTP_DIR}}"
      user_pwd: [admin, root]  # user: admin, pw: root
      events:
        - file_received
        - file_sent
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
