# Pulls

## pnp.plugins.pull.camera.MotionEyeWatcher

Watches a motioneye directory (where the images and the movies get persisted from motioneye) to trigger some useful events
based on new / modified files. The motion event only works, when the camera is configured to persist images / movies
only when motion is triggered and not 24/7.

For example I use this plugin to publish a binary motion sensor via mqtt discovery to home assistant and upload the
images and videos to dropbox and notify me via pushbullet.

Requires extra `fswatcher`.

__Arguments__

- **path (str)**: The motioneye media directory to watch.
- **image_ext (Optional[str])**: The file extension of your image files. Default is 'jpg'. Deactivate with None.
- **movie_ext (Optional[str])**: The file extension of your movie files. Default is 'mp4'. Deactivate with None.
- **motion_cool_down (Optional[bool])**: Based on created/modified files a motion event might be triggered. After the specified time without motion, the `motion off` event will be triggered.
- **defer_modified (float, optional)**: If set greater than 0, it will defer the sending of modified events for that
    amount of time (seconds). There might be multiple flushes of a file before it is written completely to disk.
    Without defer_modified each flush will raise a modified event. Default is 0.5.

__Result__

Example of a new movie file:

```yaml
{
  event: "movie",
  source: "abs/path/to/the/movie/file.mp4"
}
```

Example of a new image file:

```yaml
{
  event: "image",
  source: "abs/path/to/the/image/file.jpg"
}
```

Example of a new motion on/off event:

```yaml
{
  event: "motion",
  state: "on"  # or "off"
}
```

__Examples__

```yaml
## Basic example - just echoing events
- name: motioneye_watcher
  pull:
    plugin: pnp.plugins.pull.camera.MotionEyeWatcher
    args:
      path: "{{env::MOTIONEYE_MEDIA_PATH}}"
      image_ext: jpg
      movie_ext: mp4
      motion_cool_down: 30s
      defer_modified: 5
  push:
    plugin: pnp.plugins.push.simple.Echo

```

```yaml
## Publishes a binary motion sensor to home assistant via mqtt discovery  ...
## ... and uploads movies to dropbox when nobody is home and motion is detected
## ... and publishes images to home assistant by a push camera

## Make sure to set the following env vars correctly:
## - MOTIONEYE_MEDIA_PATH: The path where motioneye puts the media files
## - MQTT_HOST: Your mqtt host
## - HA_HOST: Your home assistant url (incl. port)
## - HA_TOKEN: Your home assistant long lived access token
## - DROPBOX_API_KEY: Your dropbox api key
## - PUSHBULLET_API_KEY: Your pushbullet api key

udfs:
  # Defines the udf. name is the actual alias you can call in selector
  # expressions.
  # For fetching the entity of binary_sensor.somebpody_home
  - name: hass_state
    plugin: pnp.plugins.udf.hass.State
    args:
      url: "{{env::HA_URL}}"
      token: "{{env::HA_TOKEN}}"
tasks:
  # Emits events when motioneye creates / modifies image and/or movie files
  - name: motioneye_watcher
    pull:
      plugin: pnp.plugins.pull.camera.MotionEyeWatcher
      args:
        path: "{{env::MOTIONEYE_MEDIA_PATH}}"
        image_ext: jpg
        movie_ext: mp4
        motion_cool_down: 30s
        defer_modified: 5
    push:
      # Handle motion event
      # - Push on/off to mqtt for automatic home asisstant discovery
      - plugin: pnp.plugins.push.simple.Nop
        selector: "data.state if data.event == 'motion' else SUPPRESS"
        deps:
          - plugin: pnp.plugins.push.mqtt.Discovery
            selector:
              data: "lambda data: data"
              object_id: "motion01_motion"
            args:
              host: "{{env::MQTT_HOST}}"
              discovery_prefix: homeassistant
              component: binary_sensor
              config:
                name: "{{var::object_id}}"
                device_class: "motion"
                payload_on: "on"
                payload_off: "off"
      # Handle image event
      # - Push image to home assistant push camera via url
      - plugin: pnp.plugins.push.simple.Nop
        selector: "data if data.event == 'image' else SUPPRESS"
        deps:
          - plugin: pnp.plugins.push.simple.Execute
            selector:
              data:
              args:
                - "lambda data: data.source"
            args:
              command: ./push_camera.sh
              timeout: 10s
              capture: true
            deps:
              plugin: pnp.plugins.push.simple.Echo
      # Handle movie event
      # - Push movie to dropbox and notify by pushbullet, but only when nobody is home
      - plugin: pnp.plugins.push.simple.Nop
        selector: "data if data.event == 'movie' and hass_state('binary_sensor.somebody_home') == 'off' else SUPPRESS"
        deps:
          - plugin: pnp.plugins.push.storage.Dropbox
            selector:
              data: "lambda data: data.source"
              target_file_name: "lambda data: basename(data.source)"
            deps:
              - plugin: pnp.plugins.push.notify.Pushbullet
                selector: data.raw_link

```

```bash
##!/bin/bash

## Contents of push_camera.sh

IMAGE_FILE=$1

curl -X POST -F "image=@${IMAGE_FILE}" ${HA_HOST}/api/webhook/motion01
```
## pnp.plugins.pull.fitbit.Current


Requests various latest / current metrics (steps, calories, distance, ...) from the fitbit api.

Requires extra `fitbit`.

__Arguments__

- **config (str)**: The configuration file that keeps your initial and refreshed authentication tokens (see below for detailed information).
- **system (str, optional)**: The metric system to use based on your localisation (de_DE, en_US, ...). Default is your configured metric system in your fitbit account
- **resources (str or list[str])**: The resources to request (see below for detailed information)

Available resources are:

* activities/calories
* activities/caloriesBMR
* activities/steps
* activities/distance
* activities/floors
* activities/elevation
* activities/minutesSedentary
* activities/minutesLightlyActive
* activities/minutesFairlyActive
* activities/minutesVeryActive
* activities/activityCalories
* body/bmi
* body/fat
* body/weight
* foods/log/caloriesIn
* foods/log/water
* sleep/awakeningsCount
* sleep/efficiency
* sleep/minutesAfterWakeup
* sleep/minutesAsleep
* sleep/minutesAwake
* sleep/minutesToFallAsleep
* sleep/startTime
* sleep/timeInBed

__Result__

Emits a map that contains the requested resources and their associated values:

```yaml
{
  'activities/calories': 1216,
  'activities/caloriesBMR': 781,
  'activities/steps': 4048,
  'activities/distance': 3.02385,
  'activities/floors': 4,
  'activities/elevation': 12,
  'activities/minutes_sedentary': 127,
  'activities/minutes_lightly_active': 61,
  'activities/minutes_fairly_active': 8,
  'activities/minutes_very_active': 24,
  'activities/activity_calories': 484,
  'body/bmi': 23.086421966552734,
  'body/fat': 0.0,
  'body/weight': 74.8,
  'foods/log/calories_in': 0,
  'foods/log/water': 0.0,
  'sleep/awakenings_count': 0,
  'sleep/efficiency': 84,
  'sleep/minutes_after_wakeup': 0,
  'sleep/minutes_asleep': 369,
  'sleep/minutes_awake': 69,
  'sleep/minutes_to_fall_asleep': 0,
  'sleep/start_time': '21:50',
  'sleep/time_in_bed': 438
}
```

__Authentication__

To request data from the fitbit account it is necessary to create an app. Go to [dev.fitbit.com](dev.fitbit.com).
Under `Manage` go to `Register an App`.
For the application website and organization website, name it anything starting with `http://` or `https://`.
Secondly, make sure the OAuth 2.0 Application Type is `Personal`.
Lastly, make sure the Callback URL is `http://127.0.0.1:8080/` in order to get our Fitbit API to connect properly.
After that, click on the agreement box and submit. You will be redirected to a page that contains your `Client ID` and
your `Client Secret`.

Next we need to acquire your initial `access`- and `refresh`-token.

```
git clone https://github.com/orcasgit/python-fitbit.git
cd python-fitbit
python3 -m venv venv
source venv/bin/activate
pip install -r dev.txt
./gather_keys_oauth2.py <client_id> <client_secret>
```

You will be redirected to your browser and asked to login to your fitbit account. Next you can restrict the app to
certain data. If everything is fine, your console window should print your `access`- and `refresh`-token and also
`expires_at`.

Put your `client_id`, `client_secret`, `access_token`, `refresh_token` and `expires_at` to a yaml file and use this
file-path as the `config` argument of this plugin. Please see the example below:

```yaml
access_token: <access_token>
client_id: <client_id>
client_secret: <client_secret>
expires_at: <expires_at>
refresh_token: <refresh_token>
```

That's it. If your token expires it will be refreshed automatically by the plugin.

__Examples__

```yaml
## Please point your environment variable `FITBIT_AUTH` to your authentication
## configuration
- name: fitbit_current
  pull:
    plugin: pnp.plugins.pull.fitbit.Current
    args:
      config: "{{env::FITBIT_AUTH}}"
      instant_run: true
      interval: 5m
      resources:
        - 'activities/calories'
        - 'activities/caloriesBMR'
        - 'activities/steps'
        - 'activities/distance'
        - 'activities/floors'
        - 'activities/elevation'
        - 'activities/minutesSedentary'
        - 'activities/minutesLightlyActive'
        - 'activities/minutesFairlyActive'
        - 'activities/minutesVeryActive'
        - 'activities/activityCalories'
        - 'body/bmi'
        - 'body/fat'
        - 'body/weight'
        - 'foods/log/caloriesIn'
        - 'foods/log/water'
        - 'sleep/awakeningsCount'
        - 'sleep/efficiency'
        - 'sleep/minutesAfterWakeup'
        - 'sleep/minutesAsleep'
        - 'sleep/minutesAwake'
        - 'sleep/minutesToFallAsleep'
        - 'sleep/startTime'
        - 'sleep/timeInBed'
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.fitbit.Devices


Requests details (battery, model, ...) about your fitbit devices / trackers associated to your account.

Requires extra `fitbit`.

__Arguments__

- **config (str)**: The configuration file that keeps your initial and refreshed authentication tokens (see below for detailed information).
- **system (str, optional)**: The metric system to use based on your localisation (de_DE, en_US, ...). Default is your configured metric system in your fitbit account

__Result__

Emits a list that contains your available trackers and/or devices and their associated details:

```yaml
[{
  'battery': 'Empty',
  'battery_level': 10,
  'device_version': 'Charge 2',
  'features': [],
  'id': 'abc',
  'last_sync_time': '2018-12-23T10:47:40.000',
  'mac': 'AAAAAAAAAAAA',
  'type': 'TRACKER'
}, {
  'battery': 'High',
  'battery_level': 95,
  'device_version': 'Blaze',
  'features': [],
  'id': 'xyz',
  'last_sync_time': '2019-01-02T10:48:39.000',
  'mac': 'FFFFFFFFFFFF',
  'type': 'TRACKER'
}]
```

__Authentication__

To request data from the fitbit account it is necessary to create an app. Go to [dev.fitbit.com](dev.fitbit.com).
Under `Manage` go to `Register an App`.
For the application website and organization website, name it anything starting with `http://` or `https://`.
Secondly, make sure the OAuth 2.0 Application Type is `Personal`.
Lastly, make sure the Callback URL is `http://127.0.0.1:8080/` in order to get our Fitbit API to connect properly.
After that, click on the agreement box and submit. You will be redirected to a page that contains your `Client ID` and
your `Client Secret`.

Next we need to acquire your initial `access`- and `refresh`-token.

```
git clone https://github.com/orcasgit/python-fitbit.git
cd python-fitbit
python3 -m venv venv
source venv/bin/activate
pip install -r dev.txt
./gather_keys_oauth2.py <client_id> <client_secret>
```

You will be redirected to your browser and asked to login to your fitbit account. Next you can restrict the app to
certain data. If everything is fine, your console window should print your `access`- and `refresh`-token and also
`expires_at`.

Put your `client_id`, `client_secret`, `access_token`, `refresh_token` and `expires_at` to a yaml file and use this
file-path as the `config` argument of this plugin. Please see the example below:

```yaml
access_token: <access_token>
client_id: <client_id>
client_secret: <client_secret>
expires_at: <expires_at>
refresh_token: <refresh_token>
```

That's it. If your token expires it will be refreshed automatically by the plugin.

__Examples__

```yaml
## Please point your environment variable `FITBIT_AUTH` to your authentication
## configuration
- name: fitbit_devices
  pull:
    plugin: pnp.plugins.pull.fitbit.Devices
    args:
      config: "{{env::FITBIT_AUTH}}"
      instant_run: true
      interval: 5m
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.fitbit.Goal

Requests your goals (water, steps, ...) from the fitbit api.

Requires extra `fitbit`.

__Arguments__

- **config (str)**: The configuration file that keeps your initial and refreshed authentication tokens (see below for detailed information).
- **system (str, optional)**: The metric system to use based on your localisation (de_DE, en_US, ...). Default is your configured metric system in your fitbit account
- **goals (str, list[str])**: The goals to request (see below for detailed information)

Available goals are:

- body/fat
- body/weight
- activities/daily/activeMinutes
- activities/daily/caloriesOut
- activities/daily/distance
- activities/daily/floors
- activities/daily/steps
- activities/weekly/distance
- activities/weekly/floors
- activities/weekly/steps
- foods/calories
- foods/water

__Result__

Emits a dictionary structure that consists of the requested goals:

```yaml
{
  'body/fat': 15.0,
  'body/weight': 70.0,
  'activities/daily/active_minutes': 30,
  'activities/daily/calories_out': 2100,
  'activities/daily/distance': 5.0,
  'activities/daily/floors': 10,
  'activities/daily/steps': 6000,
  'activities/weekly/distance': 5.0,
  'activities/weekly/floors': 10.0,
  'activities/weekly/steps': 6000.0,
  'foods/calories': 2220,
  'foods/water': 1893
}
```

__Authentication__

To request data from the fitbit account it is necessary to create an app. Go to [dev.fitbit.com](dev.fitbit.com).
Under `Manage` go to `Register an App`.
For the application website and organization website, name it anything starting with `http://` or `https://`.
Secondly, make sure the OAuth 2.0 Application Type is `Personal`.
Lastly, make sure the Callback URL is `http://127.0.0.1:8080/` in order to get our Fitbit API to connect properly.
After that, click on the agreement box and submit. You will be redirected to a page that contains your `Client ID` and
your `Client Secret`.

Next we need to acquire your initial `access`- and `refresh`-token.

```
git clone https://github.com/orcasgit/python-fitbit.git
cd python-fitbit
python3 -m venv venv
source venv/bin/activate
pip install -r dev.txt
./gather_keys_oauth2.py <client_id> <client_secret>
```

You will be redirected to your browser and asked to login to your fitbit account. Next you can restrict the app to
certain data. If everything is fine, your console window should print your `access`- and `refresh`-token and also
`expires_at`.

Put your `client_id`, `client_secret`, `access_token`, `refresh_token` and `expires_at` to a yaml file and use this
file-path as the `config` argument of this plugin. Please see the example below:

```yaml
access_token: <access_token>
client_id: <client_id>
client_secret: <client_secret>
expires_at: <expires_at>
refresh_token: <refresh_token>
```

That's it. If your token expires it will be refreshed automatically by the plugin.

__Examples__

```yaml
## Please point your environment variable `FITBIT_AUTH` to your authentication
## configuration
- name: fitbit_goal
  pull:
    plugin: pnp.plugins.pull.fitbit.Goal
    args:
      config: "{{env::FITBIT_AUTH}}"
      instant_run: true
      interval: 5m
      goals:
        - body/fat
        - body/weight
        - activities/daily/activeMinutes
        - activities/daily/caloriesOut
        - activities/daily/distance
        - activities/daily/floors
        - activities/daily/steps
        - activities/weekly/distance
        - activities/weekly/floors
        - activities/weekly/steps
        - foods/calories
        - foods/water
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.fs.FileSystemWatcher

Watches the given directory for changes like created, moved, modified and deleted files. If `ignore_directories` is
set to False, then directories will be reported as well.

Per default will recursively report any file that is touched, changed or deleted in the given path. The
directory itself or subdirectories will be object to reporting too, if `ignore_directories` is set to False.

Requires extra `fswatcher`.

__Arguments__

- **path (str)**: The path to track for file / directory changes.
- **recursive (bool, optional)**: If set to True, any subfolders of the given path will be tracked too.
    Default is True.
- **patterns (str or list, optional)**: Any file pattern (e.g. *.txt or [*.txt, *.md].
    If set to None no filter is applied. Default is None.
- **ignore_patterns (str or list, optional)**: Any patterns to ignore (specify like argument `patterns`).
    If set to None, nothing will be ignored. Default is None.
- **ignore_directories (str, optional)**: If set to True will send events for directories when file change.
    Default is False.
- **case_sensitive (bool, optional)**: If set to True, any pattern is case_sensitive, otherwise it is case insensitive.
    Default is False.
- **events (str or list, optional)**: The events to track. One or multiple of 'moved', 'deleted', 'created'
    and/or 'modified'. If set to None all events will be reported. Default is None.
- **load_file (bool, optional)**: If set to True the file contents will be loaded into the result. Default is False.
- **mode (str, optional)**: Open mode of the file (only necessary when load_file is True). Can be text, binary or auto
    (guessing). Default is auto.
- **base64 (bool, optional)**: If set to True the loaded file contents will be converted to base64 (only applicable when
    load_file is True). Argument `mode` will be automatically set to 'binary'. Default is False.
- **defer_modified (float, optional)**: If set greater than 0, it will defer the sending of modified events for that
    amount of time (seconds). There might be multiple flushes of a file before it is written completely to disk.
    Without defer_modified each flush will raise a modified event. Default is 0.5.

__Result__

Example of an emitted message

```yaml
{
    'operation': 'modified',
    'source': '/tmp/abc.txt',
    'is_directory': False,
    'destination': None,  # Only non-None when operation = 'moved'
    'file': {  # Only present when load_file is True
        'file_name': 'abc.txt',
        'content': 'foo and bar',
        'read_mode': 'text',
        'base64': False
    }
}
```

__Examples__

```yaml
- name: file_watcher
  pull:
    plugin: pnp.plugins.pull.fs.FileSystemWatcher
    args:
      path: "/tmp"
      ignore_directories: true
      events: [created, deleted, modified]
      load_file: false
  push:
    plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.fs.Size

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
## pnp.plugins.pull.ftp.Server

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
## pnp.plugins.pull.gpio.Watcher

Listens for low/high state changes on the configured gpio pins.

In more detail the plugin can raise events when one of the following situations occur:

* rising (high) of a gpio pin - multiple events may occur in a short period of time
* falling (low) of a gpio pin - multiple events may occur in a short period of time
* switch of gpio pin - will suppress multiple events a defined period of time (bounce time)
* motion of gpio pin - will raise the event `motion_on` if the pin rises and set a timer with a configurable amount of
time. Any other gpio rising events will reset the timer. When the timer expires the `motion_off` event is raised.

Requires extra `gpio`.

__Arguments__

- **pins (list)**: The gpio pins to observe for state changes. Please see the examples section on how to configure it.
- **default (on of [rising, falling, switch, motion]**: The default edge that is applied when not configured. Please see the examples section for further details.

__Result__

```yaml
{
    "gpio_pin": 17  # The gpio pin which state has changed
    "event": rising  # One of [rising, falling, switch, motion_on, motion_off]
}
```

__Examples__

```yaml
- name: gpio
  pull:
    plugin: pnp.plugins.pull.gpio.Watcher
    args:
      default: rising
      pins:
        - 2               # No mode specified: Default mode (in this case 'rising')
        - 2               # Duplicates will get ignored
        - 3:rising        # Equal to '3' (without explicit mode)
        - 3:falling       # Get the falling event for gpio pin 3 as well
        - 4:switch        # Uses some debouncing magic and emits only one rising event
        - 5:switch(1000)  # Specify debounce in millseconds (default is 500ms)
        - 5:switch(500)   # Duplicates - even when they have other arguments - will get ignored
        - 7:motion        # Uses some delay magic to emit only one motion on and one motion off event
        - 9:motion(1m)    # Specify delay (default is 30 seconds)
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.hass.State

Connects to the `home assistant` websocket api and listens for state changes. If no `include` or `exclude` is defined
it will report all state changes. If `include` is defined only entities that match one of the specified patterns will
be emitted. If `exclude` if defined entities that match at least one of the specified patterns will be ignored. `exclude`
patterns overrides `include` patterns.


__Arguments__

- **host (str)**: Url to your `home assistant` instance (e.g. http://my-hass:8123)
- **token (str)**: Your long lived access token to access the websocket api. See below for further instructions
- **include (str or list[str])**: Patterns of entity state changes to include. All state changes that do not match the
defined patterns will be ignored</br>
- **exclude (str or list[str]**:Patterns of entity state changes to exclude. All state changes that do match the defined
patterns will be ignored

Hints:
* `include` and `exclude` support wildcards (e.g `*` and `?`)
* `exclude` overrides `include`. So you can `include` everything from a domain (`sensor.*`) but exclude individual entities.
* Create a long lived access token: [Home Assistant documentation](https://developers.home-assistant.io/docs/en/auth_api.html#long-lived-access-token)

__Result__

The emitted result always contains the `entity_id`, `new_state` and `old_state`:

```yaml
{
  'entity_id': 'light.bedroom_lamp',
  'old_state': {
    'state': 'off',
    'attributes': {},
    'last_changed': '2019-01-08T18:24:42.087195+00:00',
    'last_updated': '2019-01-08T18:40:40.011459+00:00'
  },
  'new_state': {
    'state': 'on',
    'attributes': {},
    'last_changed': '2019-01-08T18:41:06.329699+00:00',
    'last_updated': '2019-01-08T18:41:06.329699+00:00'
  }
}
```

__Examples__

```yaml
- name: hass_state
  pull:
    plugin: pnp.plugins.pull.hass.State
    args:
      url: http://localhost:8123
      token: "{{env::HA_TOKEN}}"
      exclude:
        - light.lamp
      include:
        - light.*
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.http.Server

Listens on the specified `port` for requests to any endpoint.
Any data passed to the endpoint will be tried to be parsed to a dictionary (json). If this is not possible
the data will be passed as is. See sections `Result` for specific payload and examples.

Remark: You will not able to make requests to the endpoint DELETE `/_shutdown` because it is used internally.

Requires extra `http-server`.

__Arguments__

- **port (int, optional)**: The port the rest server should listen to for requests. Default is 5000.
- **allowed_methods (str or list, optional)**: List of http methods that are allowed. Default is 'GET'.
- **server_impl (str, optional)**: Choose the implementation of the WSGI-Server (wraps the flask-app).
    Possible values are: [flask, gevent]. `flask` uses the internal Flask Development server. Not recommended for
    production use. `gevent` uses [gevent](http://www.gevent.org/). Default is `gevent`.

__Result__

```shell
curl -X GET 'http://localhost:5000/resource/endpoint?foo=bar&bar=baz' --data '{"baz": "bar"}'
```

```yaml
{
    'endpoint': 'resource/endpoint,
    'method': 'GET',
    'query': {'foo': 'bar', 'bar': 'baz'},
    'data': {'baz': 'bar'},
    'is_json': True
}
```

```shell
curl -X GET 'http://localhost:5000/resource/endpoint' --data 'no json obviously'
```

```yaml
{
    'endpoint': 'resource/endpoint,
    'method': 'GET',
    'query': {},
    'data': b'no json obviously',
    'is_json': False
}
```

__Examples__

```yaml
- name: rest
  pull:
    plugin: pnp.plugins.pull.http.Server
    args:
      port: 5000
      allowed_methods: [GET, POST]
  push:
    plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.monitor.Stats

Emits every `interval` various metrics / statistics about the host system. Please see the 'Result' section for available metrics.

__Result__

```yaml
{
  'cpu_count': 4,
  'cpu_freq': 2700,
  'cpu_temp': 0.0,
  'cpu_use': 80.0,
  'disk_use': 75.1,
  'load_1m': 2.01171875,
  'load_5m': 1.89501953125,
  'load_15m': 1.94189453125,
  'memory_use': 67.0,
  'rpi_cpu_freq_capped': 0,
  'rpi_temp_limit_throttle': 0,
  'rpi_throttle': 0,
  'rpi_under_voltage': 0,
  'swap_use': 36.1
}
```

__Examples__

```yaml
- name: stats
  pull:
    plugin: pnp.plugins.pull.monitor.Stats
    args:
      interval: 10s
      instant_run: true
  push:
    plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.mqtt.Subscribe

Pulls messages from the specified topic from the given mosquitto mqtt broker (identified by host and port).

__Arguments__

- **host (str)**: Host where the mosquitto broker is running.
- **port (int)**: Port where the mosquitto broker is listening.
- **topic (str)**: Topic to pull messages from.
    You can listen to multiple topics by using the #-wildcard (e.g. `test/#` will listen to all topics underneath test).

All arguments can be automatically injected via environment variables with `MQTT` prefix (e.g. MQTT_HOST).

__Result__

The emitted message will look like this:
```yaml
{
    'topic': 'test/device/device1',
    'levels': ['test', 'device', 'device1']
    'payload': 'The actual event message'
}
```

__Examples__

```yaml
- name: mqtt
  pull:
    plugin: pnp.plugins.pull.mqtt.Subscribe
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    plugin: pnp.plugins.push.simple.Echo

```

## pnp.plugins.pull.net.PortProbe

Periodically establishes socket connection to check if anybody is listening on a given
server on a specific port.

__Arguments__

- **port (int)**: The port to probe if something is listening.</br>
- **server (str, optional)**: Server name or ip address. Default is localhost.<br/>
- **timeout (float, optional)**: Timeout for remote operations. Default is 1.0.

__Result__

```yaml
{
    "server": "www.google.de",
    "port": 80,
    "reachable": True
}
```

__Examples__

```yaml
- name: port_probe
  pull:
    plugin: pnp.plugins.pull.net.PortProbe
    args:
      server: localhost  # Server name or ip address, default is localhost
      port: 9999  # The port to probe if somebody is listening
      interval: 5s  # Probe the port every five seconds ...
      instant_run: true  # ... and run as soon as pnp starts
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.sensor.DHT

Periodically polls a dht11 or dht22 (aka am2302) for temperature and humidity readings.
Polling interval is controlled by `interval`.

Requires extra `dht`.

__Arguments__

- **device (str, optional)**: The device to poll (one of dht22, dht11, am2302). Default is 'dht22'.
- **data_gpio (int, optional)**: The data gpio port where the device operates on. Default is 17.</br>
- **humidity_offset (float, optional)**: Positive/Negative offset for humidity. Default is 0.0.</br>
- **temp_offset (float, optional)**: Positive/Negative offset for temperature. Default is 0.0.

__Result__

```yaml
{
    "humidity": 65.4  # in %
    "temperature": 23.7  # in celsius
}
```

__Examples__

```yaml
- name: dht
  pull:
    plugin: pnp.plugins.pull.sensor.DHT
    args:
      device: dht22  # Connect to a dht22
      data_gpio: 17  # DHT is connected to gpio port 17
      interval: 5m  # Polls the readings every 5 minutes
      humidity_offset: -5.0  # Subtracts 5% from the humidity reading
      temp_offset: 1.0  # Adds 1 °C to the temperature reading
      instant_run: true
  push:
    - plugin: pnp.plugins.push.simple.Echo
      selector: payload.temperature  # Temperature reading
    - plugin: pnp.plugins.push.simple.Echo
      selector: payload.humidity  # Humidity reading

```
## pnp.plugins.pull.sensor.MiFlora

Periodically polls a `xiaomi miflora plant sensor` for sensor readings (temperature, conductivity, light, ...) via btle.

Requires extra `miflora`.

__Arguments__

- **mac (str)**: The device to poll identified by mac address. See below for further instructions.
- **adapter (str, optional)**: The bluetooth adapter to use (if you have more than one). Default is 'hci0' which is
 your default bluetooth device.

Start a bluetooth scan to determine the MAC addresses of the sensor (look for Flower care or Flower mate entries)
using this command:

```bash
$ sudo hcitool lescan
LE Scan ...
F8:04:33:AF:AB:A2 [TV] UE48JU6580
C4:D3:8C:12:4C:57 Flower mate
[...]
```

__Result__

Emits a dictionary that contains an entry for every sensor of the plant sensor device:

```yaml
{
  "conductivity": 800,
  "light": 2000,
  "moisture": 42,
  "battery": 72,
  "temperature": 24.2,
  "firmaware": "3.1.9"
}
```

__Examples__

```yaml
- name: miflora
  pull:
    plugin: pnp.plugins.pull.sensor.MiFlora
    args:
      mac: 'C4:7C:8D:67:50:AB'  # The mac of your miflora device
      instant_run: true
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.sensor.OpenWeather

Periodically polls weather data from the `OpenWeatherMap` api.

__Arguments__

- **api_key (str):** The api_key you got from OpenWeatherMap after registration.
- **lat (float):** Latitude. If you pass `lat`, you have to pass `lon` as well.
- **lon (float):** Longitude. If you pass `lon`, you have to pass `lat` as well.
- **city_name (str):** The name of your city. To minimize ambiguity use lat/lon or your country as a suffix,
e.g. London,GB.
- **units (str on of (metric, imperial, kelvin))**: Specify units for temperature and speed.
imperial = fahrenheit + miles/hour, metric = celsius + m/secs, kelvin = kelvin + m/secs. Default is metric.
- **tz (str, optional)**: Time zone to use for current time and last updated time. Default is your local timezone.

Remark: You have to pass whether `city_name` or `lat/lon`.

__Result__

```json
{
	"temperature": 13.03,
	"pressure": 1021,
	"humidity": 62,
	"cloudiness": 40,
	"wind": {
		"speed": 9.3,
		"deg": 300
	},
	"poll_dts": "2018-10-03T15:41:32.156930+02:00",
	"last_updated_dts": "2018-10-03T15:20:00+02:00",
	"raw": {
		"coord": {
			"lon": 10,
			"lat": 53.55
		},
		"weather": [{
			"id": 521,
			"main": "Rain",
			"description": "shower rain",
			"icon": "09d"
		}],
		"base": "stations",
		"main": {
			"temp": 13.03,
			"pressure": 1021,
			"humidity": 62,
			"temp_min": 12,
			"temp_max": 14
		},
		"visibility": 10000,
		"wind": {
			"speed": 9.3,
			"deg": 300
		},
		"clouds": {
			"all": 40
		},
		"dt": 1538572800,
		"sys": {
			"type": 1,
			"id": 4883,
			"message": 0.0202,
			"country": "DE",
			"sunrise": 1538544356,
			"sunset": 1538585449
		},
		"id": 2911298,
		"name": "Hamburg",
		"cod": 200
	}
}
```

You can consult the specification [https://openweathermap.org/current#parameter](https://openweathermap.org/current#parameter)
to checkout the documentation about the meaning of individual fields.

__Examples__

```yaml
## Make sure you export your api key with:
##   `export OPENWEATHER_API_KEY=<your_api_key>`
- name: openweather
  pull:
    plugin: pnp.plugins.pull.sensor.OpenWeather
    args:
      city_name: "Hamburg,DE"  # Alternative: pass lat and lon
      # lon: 10
      # lat: 53.55
      units: metric  # imperial (fahrenheit + miles/hour), metric (celsius + m/secs), kelvin (kelvin + m/secs)
      instant_run: true
      # tz: GMT
  push:
    plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.sensor.Sound

Listens to the microphone in realtime and searches the stream for specific sound patterns.
Practical example: I use this plugin to recognize my doorbell without tampering with the electrical device ;-)

Requires extra `sound`.

__Arguments__

- **wav_files (List[Dict])**: A list of dictionaries containing the configuration for each file that contains an original sound pattern to listen for.
The configuration consists of the following keys:
    * **path (str)**: The path to the original sound file. Absolute or relative to the pnp configuration file
    * **mode (Union[pearson,std], optional)**: Correlation/similarity method. Default is pearson. Try out which one is best for you
    * **offset (float, optional)**: Adjusts sensitivity for similarity
Positive means less sensitive; negative is more sensitive. You should try out 0.1 steps. Default is 0.0
    * **offset (dict, optional)**: Contains the cooldown configuration. Default is a cooldown period of 10 seconds and no emit of a cooldown event
        - **period (duration, optional)**: Prevents the pull to emit more than one sound detection event per cool down period. Default is 10 seconds
        - **emit_event (bool, optional)**: If set to true the end of the cooldown period will an emit as well. Default is false
- **device_index (int, optional)**: The index of the microphone device. Run `pnp_record_sound --list` to get the index.
If not specified pyAudio will try to find a capable device
- **ignore_overflow (bool, optional)**: If set to True any buffer overflows due to slow realtime processing will be ignored.
    Otherwise an exception will be thrown

Hints:
* You can list your available input devices: `pnp_record_sound --list`
* You can record a wav file from an input device: `pnp_record_sound <out.wav> <seconds_to_record> --index=<idx>`
* This one is _not_ pre-installed when using the docker image. Would be grateful if anyone can integrate it


__Result__

Will emit the event below when the correlation coefficient is above or equal the threshold.
In this case the component has detected a sound that is similar to one of the given sound patterns

```yaml
{
    "type": "sound"  # Type 'sound' means we detected a sound pattern
    "sound": ding,  # Name of the wav_file without path and extension. To differentiate if you have multiple patterns you listen to
    "corrcoef": 0.82,  # Correlation coefficient probably between [-1;+1] for pearson
    "threshold": 0.6  # Threshold influenced by sensitivity_offset
}
```

Will emit the event below when you have configured the component to send cooldown events as well.

```yaml
{
    "type": "cooldown"  # Type 'cooldown' means that we previously identified a sound pattern and the cooldown has happened
    "sound": ding,  # Name of the wav_file without path and extension. To differentiate if you have multiple patterns you listen to
}
```

__Examples__

```yaml
- name: sound_detector
  pull:
    plugin: pnp.plugins.pull.sensor.Sound
    args:
      wav_files:  # The files to compare for similarity
        - path: ding.wav  # Absolute or relative (from the config) path to the wav file
          mode: std  # Use std correlation coefficient [pearson, std]; optional default is pearson
          offset: -0.5  # Adjust sensitivity. Positive means less sensitive; negative is more sensitive. Default is 0.0
        - path: doorbell.wav  # This will use default values for mode and offset (pearson, 0.0)
          cooldown:
            period: 10s  # Prevents the pull to emit more than one sound detection event every 10 seconds
            emit_event: true  # Fire an event after the actual cool down - Useful for binary_sensors to return to their 'off' state
      device_index:  # The index of the microphone devices. If not specified pyAudio will try to find a capable device
      ignore_overflow: true  # Some devices might be too slow to process the stream in realtime. Ignore any buffer overflow errors.
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.simple.Count

Emits every `interval` seconds a counting value which runs from `from_cnt` to `to_cnt`.
If `to_cnt` is None the counter will count to infinity (or more precise to sys.maxsize).

__Arguments__

- **interval (duration literal)**: Wait the amount of seconds before emitting the next counter.
- **wait (int)**: DEPRECATED! Use `interval` instead.
- **from_cnt (int)**: Starting value of the counter.
- **to_cnt (int, optional)**: End value of the counter. If not passed set to "infinity" (precise: int.max).

__Result__

Counter value (int).

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
## pnp.plugins.pull.simple.Cron

Execute push-components based on time constraints configured by cron-like expressions.

This plugin basically wraps [cronex](https://pypi.org/project/cronex/) to parse cron expressions and to check if
any job is pending. See the documentation of `cronex` for a guide on featured/supported cron expressions.

__Arguments__

- **exppresions (List[str])**: Cron like expressions to configure the scheduler.

__Result__

Imagine your cron expressions looks like this: `*/1 * * * * every minute`.
The pull will emit every minute the same payload:

```yaml
{
  'data': 'every minute'
}
```

__Examples__

```yaml
- name: cron
  pull:
    plugin: pnp.plugins.pull.simple.Cron
    args:
      expressions:
        - "*/1 * * * * every minute"
        - "0 15 * * * 3pm"
        - "0 0 * * * midnight every day"
        - "0 16 * * 1-5 every weekday @ 4pm"
  push:
    plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.simple.Repeat

Emits every `interval` seconds the same `repeat`.

__Arguments__

- **interval (duration literal)**: Wait the amount of seconds before emitting the next `repeat`.
- **wait (int)**: DEPRECATED! Use `interval` instead.
- **repeat (any)**: The object to emit.

__Result__

Emits the `repeat`-object as it is.

__Examples__

```yaml
- name: repeat
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      repeat: "Hello World"  # Repeats 'Hello World'
      interval: 1s  # Every second
  push:
    plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.traffic.DeutscheBahn

Polls the Deutsche Bahn website using the `schiene` package to find the next trains scheduled
for a given destination from a specific origin station.


__Arguments__

- **origin (str)**: The origin station.
- **destination (str)**: The destination station.
- **only_direct (bool, optional)**: If set to True only show direct connections (without transfer). Default is False.

__Result__

```yaml
[{
	"departure": "09:01",
	"arrival": "15:09",
	"travel_time": "6:05",
	"products": ["ICE"],
	"transfers": 1,
	"canceled": false,
	"delayed": true,
	"delay_departure": 3,
	"delay_arrival": 0
}, {
	"departure": "09:28",
	"arrival": "15:39",
	"travel_time": "6:11",
	"products": ["ICE"],
	"transfers": 0,
	"canceled": false,
	"delayed": false,
	"delay_departure": 0,
	"delay_arrival": 0
}, {
	"departure": "09:36",
	"arrival": "16:02",
	"travel_time": "6:26",
	"products": ["ICE"],
	"transfers": 1,
	"canceled": false,
	"delayed": false,
	"delay_departure": 0,
	"delay_arrival": 0
}]
```

__Examples__

```yaml
- name: deutschebahn
  pull:
    plugin: pnp.plugins.pull.traffic.DeutscheBahn
    args:
      origin: Hamburg Hbf
      destination: München Hbf
      only_direct: true  # Only show direct transfers wo change. Default is False.
      instant_run: true
      interval: 1m
  push:
    plugin: pnp.plugins.push.simple.Echo

```
## pnp.plugins.pull.trigger.Web

Wraps a poll-based pull and provides a rest-endpoint to externally trigger the poll action.
This will disable the cron-like / scheduling features of the polling component and simply
provides you an interface to call the component anytime you see fit.

__Arguments__

- **poll (Polling component)**: The polling component that you want to trigger externally. See example for configuration.
- **port (int)**: The port for the server to listen on.
- **endpoint (str, optional)**: The name of the endpoint. Default is `/trigger`.

Assume you set `port = 8080` and `endpoint = trigger` then your corresponding `curl` command
to trigger the polling externally would look like this:

```bash
curl http://localhost:8080/trigger
```

In case of success you get back a `200`. In case of error it's a `500`.

__Result__

The component will simply forward the result of the underlying component to dependent pushes.

__Examples__

```yaml
engine: !engine
  type: pnp.engines.AsyncEngine
  retry_handler: !retry
    type: pnp.engines.NoRetryHandler
tasks:
  - name: trigger_web
    pull:
      plugin: pnp.plugins.pull.trigger.Web
      args:
        port: 8080
        endpoint: '/'
        poll:
          plugin: pnp.plugins.pull.monitor.Stats
    push:
      plugin: pnp.plugins.push.simple.Echo

```

Test it out:

```bash
curl http://localhost:8080/
```

```yaml
- name: trigger_web
  pull:
    plugin: pnp.plugins.pull.trigger.Web
    args:
      port: 8080
      poll:
        plugin: pnp.plugins.pull.traffic.DeutscheBahn
        args:
          origin: Hamburg Hbf
          destination: München Hbf
          only_direct: true  # Only show direct transfers wo change. Default is False.
  push:
    plugin: pnp.plugins.push.simple.Echo

```

Test it out:

```bash
curl http://localhost:8080/trigger
```
## pnp.plugins.pull.zway.ZwayPoll

Pulls the specified json content from the zway rest api. The content is specified by the url, e.g.
`http://<host>:8083/ZWaveAPI/Run/devices` will pull all devices and serve the result as a json.

Specify the polling interval by setting the argument `interval`. User / password combination is required when
your api is protected against guest access (by default it is).

Use multiple pushes and the related selectors to extract the required content like temperature readings (see
the examples section for guidance).

__Arguments__

- **url (str)**: The url to poll periodically.
- **user (str)**: Authentication user name.
- **password (str)**: Authentication password.
- **interval (polling literal, optional)**: Polling interval (default: 1m).

All arguments (`url`, `user` and `password`) can be automatically injected via environment variables.
* ZWAY_URL
* ZWAY_USER
* ZWAY_PASSWORD

__Result__

Emits the content of the fetched url as it is.

__Examples__

```yaml
## Please make sure to adjust url and device ids
## Username and Password are injected from environment variables:
##     export ZWAY_USER=admin
##     export ZWAY_PASSWORD=secret_one
- name: zway
  pull:
    plugin: pnp.plugins.pull.zway.ZwayPoll
    args:
      url: "http://smarthome:8083/ZWaveAPI/Run/devices"
      interval: 5s
  push:
    - plugin: pnp.plugins.push.simple.Echo
      # Temperature of fibaro motion sensor
      # You can access the returned json like you would inquire the zway-api
      selector: payload[19].instances[0].commandClasses[49].data[1].val.value
    - plugin: pnp.plugins.push.simple.Echo
      # Luminiscence of fibaro motion sensor
      selector: payload[19].instances[0].commandClasses[49].data[3].val.value

```

__Appendix__

Below are some common selector examples to fetch various metrics from various devices

- **Fibaro Motion Sensor**
* Temperature
`payload[deviceid].instances[0].commandClasses[49].data[1].val.value`
* Luminescence
`payload[deviceid].instances[0].commandClasses[49].data[3].val.value`

- **fibaro Wallplug**
* Meter
`payload[deviceid].instances[0].commandClasses[50].data[0].val.value`

- **Thermostat (Danfoss / other should work as well)**
* Setpoint
`payload[deviceid].instances[0].commandClasses[67].data[1].val.value`

- **Battery operated devices**
* Battery level
`payload[deviceid].instances[0].commandClasses[128].data.last.value`

## pnp.plugins.pull.zway.ZwayReceiver

Setups a http server to process incoming GET-requests from the Zway-App [`HttpGet`](https://github.com/hplato/Zway-HTTPGet/blob/master/index.js).

__Arguments__

- **url_format (str)**: The url_format that is configured in your HttpGet App. If you configured
`http://<ip>:<port>/set?device=%DEVICE%&state=%VALUE%` (default of the App), you basically have to copy the path
component `set?device=%DEVICE%&state=%VALUE%` to be your `url_format`.
- **mode ([mapping, auto, both])**: If set to `mapping` (default) you should provide the `device_mapping` to manually map your virtual devices.
If set to `auto` the plugin will try to determine the device_id, command class, mode and the type on it's own. If set to `both` the plugin
will first try the `device_mapping` and then perform the auto-magic.</br>
- **device_mapping (Or(Dict[Str, Str], Dict[Str, Dict]), optional)**: A mapping to map the somewhat cryptic virtual device names to
human readable ones. Default is None, which means that no mapping will be performed. Two ways possible:
1. Ordinary mapping from virtual device name -> alias.
2. Enhanced mapping from virtual device name to dictionary with additional properties. One property has to be alias.
- **ignore_unknown_devices (bool, optional)**: If set to True all incoming requests that are associated with an device
that is not part of the mapping or - when mode = [auto, both] - cannot be auto mapped will be ignored. Default is False.

Additionally the component will accept any arguments that `pnp.plugins.pull.http.Server` would accept.

__Result__

Given the url_format `set?%DEVICE%&value=%VALUE%`, the url `http://<ip>:<port>/set?vdevice1&value=5.5` and
the device_mapping `vdevice1 -> alias of vdevice1` the emitted message will look like this:

```yaml
{
    'device_name': 'alias of vdevice1',
    'raw_device': 'vdevice1'
    'value': '5.5',
    'props': {}
}
```

When `mode` is `auto` or `both` the plugin will try to determine the device id and the type of the virtual device on it's
own. Given the virtual device name `ZWayVDev_zway_7-0-48-1` and the value of `on` will produce the following:

```yaml
{
    'device_name': '7',
    'raw_device': 'ZWayVDev_zway_7-0-48-1',
    'value': 'on'
    'props': {
        'command_class': '48',
        'mode': '1',
        'type': 'motion'
    }
}
```

__Examples__

```yaml
- name: zway_receiver
  pull:
    plugin: pnp.plugins.pull.zway.ZwayReceiver
    args:
      port: 5000
      mode: mapping  # mapping, auto or both
      device_mapping:
        vdevice1:  # Props = {type: motion}
          alias: dev1
          type: motion
        vdevice2:  # Props = {type: switch, other_prop: foo}
          alias: dev2
          type: switch
          other_prop: foo
        vdevice3: dev3  # props == {}
      url_format: "%DEVICE%?value=%VALUE%"
      ignore_unknown_devices: false
  push:
    - plugin: pnp.plugins.push.simple.Echo
      selector: "'Got value {} from device {} ({}) with props {}'.format(data.value, data.device_name, data.raw_device, data.props)"

```
