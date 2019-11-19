# Pushes

## pnp.plugins.push.fs.FileDump

This push dumps the given `payload` to a file to the specified `directory`.
If argument `file_name` is None, a name will be generated based on the current datetime (%Y%m%d-%H%M%S).
If `file_name` is not passed (or None) you should pass `extension` to specify the extension of the generated
file name.
Argument `binary_mode` controls whether the dump is binary (mode=wb) or text (mode=w).

__Arguments__

- **directory (str, optional)**: The target directory to store the dumps. Default is '.' (current directory).
- **file_name (str, optional)**: The name of the file to dump. If set to None a file name will be automatically
    generated. You can specify the file_name via the envelope, too. Envelope will override __init__ file name.
    Default is None.
- **extension (str, optional)**: The extension to use when the file name is automatically generated. Can be overridden by
    envelope. Default is '.dump'.
- **binary_mode (bool, optional)**: If set to True the file will be written in binary mode ('wb');
    otherwise in text mode ('w'). Default is False.

__Result__

Will return an absolute path to the file created.

__Examples__

```yaml
- name: file_dump
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      repeat: "Hello World"
  push:
    plugin: pnp.plugins.push.fs.FileDump
    args:
      directory: "{{env::WATCH_DIR}}"
      file_name: null  # Auto-generated file (timestamp)
      extension: ".txt"  # Extension of auto-generated file
      binary_mode: false  # text mode
    deps:
      - plugin: pnp.plugins.push.simple.Echo

```

```yaml
- name: file_dump
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      repeat: "Hello World"
  push:
    plugin: pnp.plugins.push.fs.FileDump
    # Override `file_name` and `extension` via envelope.
    # Instead of an auto generated file, the file '/tmp/hello-world.hello' will be dumped.
    selector:
      data: "lambda data: data"
      file_name: hello-world
      extension: .hello
    args:
      directory: "{{env::WATCH_DIR}}"
      file_name: null  # Auto-generated file (timestamp)
      extension: ".txt"  # Extension of auto-generated file
      binary_mode: false  # text mode
    deps:
      - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.push.hass.Service

Calls a home assistant service providing the payload as service-data.

__Arguments__

- **url (str)**: The url to your home assistant instance (e.g. http://hass:8123)
- **token (str)**: The love live access token to get access to home assistant
- **domain (str)**: The domain the service.
- **service (str)**: The name of the service.
- **timeout (Optional[int])**: Tell the request to stop waiting for a reponse after given number of seconds. Default is 5 seconds.

__Result__

Returns the payload as-is for better chaining (this plugin can't add any useful information).

__Examples__

```yaml
## Calls the frontend.set_theme service to oscillate between a "light" and a "dark" theme
- name: hass_service
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 10s
  push:
    plugin: pnp.plugins.push.hass.Service
    selector:
      name: "lambda i: 'clear' if i % 2 == 0 else 'dark'"
    args:
      url: http://localhost:8123
      token: "{{env::HA_TOKEN}}"
      domain: frontend
      service: set_theme

```

```yaml
## Calls the notify.pushbullet service to send a message with the actual counter
- name: hass_service
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 10s
  push:
    plugin: pnp.plugins.push.hass.Service
    selector:
      message: "lambda i: 'Counter: ' + str(i)"
    args:
      url: http://localhost:8123
      token: "{{env::HA_TOKEN}}"
      domain: notify
      service: pushbullet

```
## pnp.plugins.push.http.Call

Makes a request to a http resource.

__Arguments__

- **url (str)**: Request url. Can be overridden via envelope.
- **method (str, optional)**: The http method to use for the request. Must be a valid http method (GET, POST, ...).
    Default is 'GET'. Can be overridden via envelope.
- **fail_on_error (bool, optional)**: If True the push will fail on a http status code <> 2xx. This leads to an error
    message recorded into the logs and no further execution of any dependencies. Default is False. Can be overridden
    by the envelope.
- **provide_response (bool, optional)**: If True the push will _not_ return the payload as it is, but instead provide the
    response status_code, fetched url content and a flag if the url content is a json response. This is useful for
    other push instances in the dependency chain. Default is False.

__Result__

Will return the payload as it is for easy chaining of dependencies.
If `provide_response` is True the push will return a dictionary that looks like this:

```yaml
{
    "status_code": 200,
    "data": "fetched url content",
    "is_json": False
}
```

Please note that this structure will be interpreted as an envelope with the keys `status_code` and `is_json` along with
the payload 'fetched url content' by other push instances in the dependency chain.

__Examples__

```yaml
## Simple example calling the built-in rest server
## Oscillates between http method GET and POST. Depending on the fact if the counter is even or not.
- name: http_call
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 5s
  push:
    plugin: pnp.plugins.push.http.Call
    selector:
      data:
        counter: "lambda data: data"
      method: "lambda data: 'POST' if int(data) % 2 == 0 else 'GET'"
    args:
      url: http://localhost:5000/
- name: rest_server
  pull:
    plugin: pnp.plugins.pull.http.Server
    args:
      port: 5000
      allowed_methods:
        - GET
        - POST
  push:
    plugin: pnp.plugins.push.simple.Echo

```

```yaml
## Demonstrates the use of `provide_response` set to True.
## Call will return a response object to dependent push instances.
- name: http_call
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 5s
  push:
    plugin: pnp.plugins.push.http.Call
    args:
      url: http://localhost:5000/
      provide_response: true
    deps:
      plugin: pnp.plugins.push.simple.Echo
- name: rest_server
  pull:
    plugin: pnp.plugins.pull.http.Server
    args:
      port: 5000
      allowed_methods:
        - GET
  push:
    plugin: pnp.plugins.push.simple.Nop

```
## pnp.plugins.push.mail.GMail

Sends an e-mail via the `gmail api`.

__Arguments__

- **token_file (str)**: The file that contains your tokens. See below for further details
- **recipient (str or List[str])**: The recipient (to) of the e-mail. Optionally you can pass a list for multiple recipients.
    Can be overridden via envelope.
- **subject (str, optional)**: Sets the subject of the e-mail. Default is None, which means the subject is expected
    to be set by the envelope. Can be overridden by the envelope.
- **sender (str, optional)**: Sets the sender of the e-mail. Default is 'pnp'. Can be overridden by the envelope.
- **attachment (str, optional)**: Can be set by the envelope. If set the `attachment` should point to a valid file to
    attach to the e-mail. Default is None which means not to attach a file.

__Tokens__

Goto [https://console.developers.google.com](https://console.developers.google.com) and create a new project.
Goto `Dashboard` and click `Enable API's and Services`. Search `gmail` and enable the api.
Goto `Credentials`, then `OAuth consent screen` and set the `Application Name`. Save the form.
Goto `Credentials` and select `Create credentials` and `OAuth client id`. Select `Other` and name it as you wish.
Afterwards download your credentials as a json file.
Run `pnp_gmail_tokens <credentials.json> <out_tokens.pickle>`.
You will be requested to login to your GMail account and accept the requested scopes (sending mails on your behalf).
If this went well, the tokens for your previously downloaded credentials will be created.
The `<out_tokens.pickle>` is the file you have to pass as the `token_file` to this component.

__Result__

Will return the payload as it is for easy chaining of dependencies.

__Examples__

```yaml
## Pull triggers when a file is created in the specified directory
## The GMail push will send an e-mail to a specific recipient with the created file attached
- name: gmail
  pull:
    plugin: pnp.plugins.pull.fs.FileSystemWatcher
    args:
      path: "/tmp"
      ignore_directories: true
      events:
        - created
      load_file: false
  push:
    plugin: pnp.plugins.push.mail.GMail
    selector:
      subject: "lambda p: basename(p.source)"  # basename(p.source) = file name
      data:  # Message body -> None -> Just the attachment
      attachment: "lambda p: p.source"  # Attachment -> p.source = absolute path
    args:
      token_file: "{{env::GMAIL_TOKEN_FILE}}"
      recipient: "{{env::GMAIL_RECIPIENT}}"  # Overridable with envelope
      subject: "Override me"  # Overridable with envelope
      sender: "pnp"  # Overridable with envelope

```
## pnp.plugins.push.ml.FaceR

FaceR (short one for face recognition) tags known faces in images. Output is the image with all faces tagged whether
with the known name or an `unknown_label`. Default for unknown ones is 'Unknown'.

Known faces can be ingested either by a directory of known faces (`known_faces_dir`) or by mapping of `known_faces`
(dictionary: name -> [list of face files]).

The `payload` passed to the `push` method is expected to be a valid byte array that represents an image in memory.

Hint: This one is _not_ pre-installed when using the docker image. Would be grateful if anyone can integrate it

__Arguments__

- **known_faces (dict<str, file_path as str>, optional)**: Mapping of a person's name to a list of images that contain
    the person's face. Default is None.
- **known_faces_dir (str, optional)**: A directory containing images with known persons (file_name -> person's name).
    Default is None.
- **unknown_label (str, optional)**: Tag label of unknown faces. Default is 'Unknown'.
- **lazy (bool, optional)**: If set to True the face encodings will be loaded when the first push is executed (lazy);
    otherwise the encodings are loaded when the plugin is initialized (during `__init__`).

You have to specify either `known_faces` or `known_faces_dir`. If both are unsupplied the push will fail.

__Result__

Will return a dictionary that contains the bytes of the tagged image (key `tagged_image`) and metadata (`no_of_faces`,
`known_faces`)

```yaml
{
    'tagged_image': <bytes of tagged image>
    'no_of_faces': 2
    'known_faces': ['obama']
}
```

__Examples__

```yaml
- name: faceR
  pull:
    plugin: pnp.plugins.pull.fs.FileSystemWatcher
    args:
      path: "/tmp/camera"
      recursive: true
      patterns: "*.jpg"
      ignore_directories: true
      case_sensitive: false
      events: [created]
      load_file: true
      mode: binary
      base64: false
  push:
    plugin: pnp.plugins.push.ml.FaceR
    args:
      known_faces_dir: "/tmp/faces"
      unknown_label: "don't know him"
      lazy: true

```
## pnp.plugins.push.mqtt.Discovery

TBD

[https://www.home-assistant.io/docs/mqtt/discovery/](https://www.home-assistant.io/docs/mqtt/discovery/)

__Arguments__

TBD

__Result__

For chaining of pushes the payload is simply returned as is.

__Examples__

```yaml
## Please point your environment variable `FITBIT_AUTH` to your authentication configuration
- name: fitbit_steps
  pull:
    plugin: pnp.plugins.pull.fitbit.Current
    args:
      config: "{{env::FITBIT_AUTH}}"
      instant_run: true
      interval: 5m
      resources:
        - activities/steps
  push:
    - plugin: pnp.plugins.push.mqtt.Discovery
      selector: "data.get('activities/steps')"
      args:
        host: localhost
        discovery_prefix: homeassistant
        component: sensor
        object_id: fitbit_steps
        config:
          name: "{{var::object_id}}"
          icon: "mdi:soccer"

- name: fitbit_devices_battery
  pull:
    plugin: pnp.plugins.pull.fitbit.Devices
    args:
      config: "{{env::FITBIT_AUTH}}"
      instant_run: true
      interval: 5m
  push:
    - plugin: pnp.plugins.push.mqtt.Discovery
      selector:
        data: "lambda data: data.get('battery_level')"
        object_id: "lambda data: 'fb_{}_battery'.format(data.get('device_version', '').replace(' ', '_').lower())"
      unwrap: true
      args:
        host: localhost
        discovery_prefix: homeassistant
        component: sensor
        config:
          name: "{{var::object_id}}"
          device_class: "battery"
          unit_of_measurement: "%"
    - plugin: pnp.plugins.push.mqtt.Discovery
      selector:
        data: "lambda data: data.get('last_sync_time')"
        object_id: "lambda data: 'fb_{}_lastsync'.format(data.get('device_version', '').replace(' ', '_').lower())"
      unwrap: true
      args:
        host: localhost
        discovery_prefix: homeassistant
        component: sensor
        config:
          name: "{{var::object_id}}"

```
## pnp.plugins.push.mqtt.Publish

Will push the given `payload` to a mqtt broker (in this case mosquitto).
The broker is specified by `host` and `port`. In addition a topic needs to be specified were the payload
is pushed to (e.g. home/living/thermostat).

The `payload` will be pushed as it is. No transformation is applied. If you need to some transformations, use the
selector.

__Arguments__

- **host (str)**: The host where the mosquitto broker is running.
- **port (int, optional)**: The port where the mosquitto broker is listening. Default is 1883.
- **topic (str, optional)**: The topic to subscribe to. If set to None the envelope of the
    payload has to contain a 'topic' key or the push will fail (default is None). If both exists
    the topic from the envelope will overrule the __init__ one.
- **retain (bool, optional)**: If set to True will mark the message as retained. Default is False.
    See the mosquitto man page for further guidance
    [https://mosquitto.org/man/mqtt-7.html](https://mosquitto.org/man/mqtt-7.html).
- **multi (bool, optional)**: If set to True the payload is expected to be a dictionary. Each item of that dictionary will
be send individually to the broker. The key of the item will be appended to the configured topic. The value of the item
is the actual payload. Default is False.

__Result__

For chaining of pushes the payload is simply returned as is.

__Examples__

```yaml
- name: mqtt
  pull:
    plugin: pnp.plugins.pull.simple.Count
  push:
    # Will push the counter to the 'home/counter/state' topic
    plugin: pnp.plugins.push.mqtt.Publish
    args:
      host: localhost
      topic: home/counter/state
      port: 1883
      retain: true

```

```yaml
- name: mqtt
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 1s
  push:
    plugin: pnp.plugins.push.mqtt.Publish
    # Lets override the topic via envelope mechanism
    # Will publish even counts on topic 'even' and uneven counts on 'uneven'
    selector:
      data: "lambda data: data"
      topic: "lambda data: 'test/even' if int(data) % 2 == 0 else 'test/uneven'"
    args:
      host: localhost
      port: 1883

```

```yaml
- name: mqtt
  pull:
    # Periodically gets metrics about your system
    plugin: pnp.plugins.pull.monitor.Stats
    args:
      instant_run: true
      interval: 10s
  push:
    # Push them to the mqtt
    plugin: pnp.plugins.push.mqtt.Publish
    args:
      host: localhost
      topic: devices/localhost/
      port: 1883
      retain: true
      # Each item of the payload-dict (cpu_count, cpu_usage, ...) will be pushed to the broker as multiple items.
      # The key of the item will be appended to the topic, e.g. `devices/localhost/cpu_count`.
      # The value of the item is the actual payload.
      multi: true

```
## pnp.plugins.push.notify.Pushbullet

Sends a message to the [Pushbullet](http://www.pushbullet.com) service.
The type of the message will guessed:

* `push_link` for a single http link
* `push_file` if the link is directed to a file (mimetype will be guessed)
* `push_note` for everything else (converted to `str`)

Requires extra `pushbullet`.

__Arguments__

- **api_key (str)**: The api key to your pushbullet account.
- **title (str, optional)**: The title to use for your messages. Defaults to `pnp`</br>

__Result__

Will return the payload as it is for easy chaining of dependencies.

__Examples__

```yaml
## Make sure that you provided PUSHBULETT_API_KEY as an environment variable
- name: pushbullet
  pull:
    plugin: pnp.plugins.pull.fs.FileSystemWatcher
    args:
      path: "/tmp"
      ignore_directories: true
      events:
        - created
      load_file: false
  push:
    plugin: pnp.plugins.push.notify.Pushbullet
    args:
      title: "Watcher"
    selector: "'New file: {}'.format(data.source)"

```
## pnp.plugins.push.notify.Slack

Sends a message to a given [Slack](http://www.slack.com) channel.

You can specify the channel, the name of the poster, the icon of the poster
and a list of users to ping.

__Arguments__

- **api_key (str)**: The api key of your slack oauth token
- **channel (str)**: The channel to post the message to
- **username (str, optional)**: The username of the message poster. Defaults to PnP
- **emoji (str, optional)**: The emoji of the message poster. Defaults to :robot:
- **ping_users (List[str], optional)**: A list of users to ping when the message is posted. By default non one is ping'd.

You can override the `channel`, `username`, `emoji` and the `ping_users` list by the envelope. See the example for more details.

__Result__

Will return the payload as it is for easy chaining of dependencies.

__Examples__

```yaml
- name: slack
  pull:
    plugin: pnp.plugins.pull.simple.Count  # Let's count
    args:
      wait: 10
  push:
    - plugin: pnp.plugins.push.notify.Slack
      selector:
        data: "lambda data: 'This is the counter: {}'.format(data)"
        # You can override the channel if necessary
        # channel: "lambda data: 'test_even' if int(data) % 2 == 0 else 'test_odd'"
        # You can override the username if necessary
        # username: the_new_user
        # You can override the emoji if necessary
        # emoji: ':see_no_evil:'
        # You can override the ping users if necessary
        # ping_users:
        #   - clone_dede
      args:
        api_key: "{{env::SLACK_API_KEY}}"  # Your slack api key.
        channel: test  # The channel to post to. Mandatory. Overridable by envelope.
        username: slack_tester  # The username to show. Default is PnP. Overridable by envelope
        emoji: ':pig:'  # The emoji to use. Default is :robot: . Overridable by envelope
        ping_users:  # The users you want to ping when the message is send. Overridable by envelope
          - dede

```
## pnp.plugins.push.simple.Echo

Simply log the passed payload to the default logging instance.

__Arguments__

None.

__Result__

Will return the payload as it is for easy chaining of dependencies.

__Examples__

```yaml
- name: count
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      interval: 1s
      from_cnt: 1
      to_cnt: 10
  push:
    plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.push.simple.Execute

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
## pnp.plugins.push.simple.Wait

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
## pnp.plugins.push.storage.Dropbox

Uploads provided file to the specified dropbox account.

__Arguments__

- **api_key (str)**: The api key to your dropbox account/app.
- **target_file_name (str, optional)**: The file path on the server where to upload the file to.
If not specified you have to specify this argument during push time by setting it in the envelope.
- **create_shared_link (bool, optional)**: If set to True, the push will create a publicly available link to your uploaded file. Default is `True`.

Requires extra `dropbox`.

__Result__

Returns a dictionary that contains metadata information about your uploaded file. If you uploaded a file named `42.txt`,
your result will be similiar to the one below:

```yaml
{
    "name": "42.txt",
    "id": "HkdashdasdOOOOOadss",
    "content_hash": "aljdhfjdahfafuhu489",
    "size": 42,
    "path": "/42.txt",
    "shared_link": "http://someserver/tosomestuff/asdasd?dl=1",
    "raw_link": "http://someserver/tosomestuff/asdasd?raw=1"
}
```

`shared_link` is the one that is publicly available (if you know the link). Same for `raw_link`, but this link will return
the raw file (without the dropbox overhead). Both are `None` if `create_shared_link` is set to `False`.

__Examples__

```yaml
## Make sure that you provided DROPBOX_API_KEY as an environment variable
- name: dropbox
  pull:
    plugin: pnp.plugins.pull.fs.FileSystemWatcher
    args:
      path: "/tmp"
      ignore_directories: true
      events:
        - created
        - modified
      load_file: false
  push:
    - plugin: pnp.plugins.push.storage.Dropbox
      args:
        create_shared_link: true  # Create a publicly available link
      selector:
        data: "lambda data: data.source"  # Absolute path to file
        target_file_name: "lambda data: basename(data.source)"  # File name only

```
## pnp.plugins.push.timedb.InfluxPush

Pushes the given `payload` to an influx database using the line `protocol`.
You have to specify `host`, `port`, `user`, `password` and the `database`.

The `protocol` is basically a string that will be augmented at push-time with data from the payload.
E.g. {payload.metric},room={payload.location} value={payload.value} assumes that payload contains metric, location
and value.
See [https://docs.influxdata.com/influxdb/v1.5/write_protocols/line_protocol_tutorial/](https://docs.influxdata.com/influxdb/v1.5/write_protocols/line_protocol_tutorial/)

__Arguments__

- **host (str)**: The host where the influxdb is running.
- **port (int)**: The port where the influxdb service is listening on.
- **user (str)**: Username to use for authentication.
- **password (str)**: Related password.
- **database (str)**: The database to write to.
- **protocol (str)**: Line protocol template (augmented with payload-data).

All arguments can be automatically injected via environment variables with `INFLUX` prefix (e.g. `INFLUX_HOST`).

__Result__

For the ability to chain multiple pushes together the payload is simply returned as is.

__Examples__

```yaml
- name: influx_push
  pull:
    plugin: pnp.plugins.pull.mqtt.Subscribe
    args:
      host: mqtt
      topic: home/#
  push:
    plugin: pnp.plugins.push.timedb.InfluxPush
    selector:
      data: "lambda data: data"
    args:
      host: influxdb
      port: 8086
      user: root
      password: secret
      database: home
      protocol: "{payload.levels[2]},room={payload.levels[1]} {payload.levels[3]}={payload.payload}"

```
