# Plugins

## pnp.plugins.pull.fitbit.Current


Requests various latest / current metrics (steps, calories, distance, ...) from the fitbit api.

Requires extra `fitbit`.

__Arguments__

**config (str)**: The configuration file that keeps your initial and refreshed authentication tokens (see below for detailed information).<br/>
**system (str, optional)**: The metric system to use based on your localisation (de_DE, en_US, ...). Default is your configured metric system in your fitbit account<br/>
**resources (str or list[str])**: The resources to request (see below for detailed information)

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
## Please point your environment variable `FITBIT_AUTH` to your authentication configuration

- name: fitbit_current
  pull:
    plugin: pnp.plugins.pull.fitbit.Current
    args:
      config: "{{env::FITBIT_AUTH}}"
      instant_run: True
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

**config (str)**: The configuration file that keeps your initial and refreshed authentication tokens (see below for detailed information).<br/>
**system (str, optional)**: The metric system to use based on your localisation (de_DE, en_US, ...). Default is your configured metric system in your fitbit account<br/>

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
## Please point your environment variable `FITBIT_AUTH` to your authentication configuration

- name: fitbit_devices
  pull:
    plugin: pnp.plugins.pull.fitbit.Devices
    args:
      config: "{{env::FITBIT_AUTH}}"
      instant_run: True
      interval: 5m
  push:
    - plugin: pnp.plugins.push.simple.Echo
```
## pnp.plugins.pull.fitbit.Goal

Requests your goals (water, steps, ...) from the fitbit api.

Requires extra `fitbit`.

__Arguments__

**config (str)**: The configuration file that keeps your initial and refreshed authentication tokens (see below for detailed information).<br/>
**system (str, optional)**: The metric system to use based on your localisation (de_DE, en_US, ...). Default is your configured metric system in your fitbit account<br/>
**goals (str, list[str])**: The goals to request (see below for detailed information)

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
## Please point your environment variable `FITBIT_AUTH` to your authentication configuration

- name: fitbit_goal
  pull:
    plugin: pnp.plugins.pull.fitbit.Goal
    args:
      config: "{{env::FITBIT_AUTH}}"
      instant_run: True
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

**path (str)**: The path to track for file / directory changes.<br/>
**recursive (bool, optional)**: If set to True, any subfolders of the given path will be tracked too.
    Default is True.<br/>
**patterns (str or list, optional)**: Any file pattern (e.g. *.txt or [*.txt, *.md].
    If set to None no filter is applied. Default is None.<br/>
**ignore_patterns (str or list, optional)**: Any patterns to ignore (specify like argument `patterns`).
    If set to None, nothing will be ignored. Default is None.<br/>
**ignore_directories (str, optional)**: If set to True will send events for directories when file change.
    Default is False.<br/>
**case_sensitive (bool, optional)**: If set to True, any pattern is case_sensitive, otherwise it is case insensitive.
    Default is False.<br/>
**events (str or list, optional)**: The events to track. One or multiple of 'moved', 'deleted', 'created'
    and/or 'modified'. If set to None all events will be reported. Default is None.<br/>
**load_file (bool, optional)**: If set to True the file contents will be loaded into the result. Default is False.<br/>
**mode (str, optional)**: Open mode of the file (only necessary when load_file is True). Can be text, binary or auto
    (guessing). Default is auto.<br/>
**base64 (bool, optional)**: If set to True the loaded file contents will be converted to base64 (only applicable when
    load_file is True). Argument `mode` will be automatically set to 'binary'. Default is False.<br/>
**defer_modified (float, optional)**: If set greater than 0, it will defer the sending of modified events for that
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
      ignore_directories: True
      events: [created, deleted, modified]
      load_file: False
  push:
    plugin: pnp.plugins.push.simple.Echo
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

**pins (list)**: The gpio pins to observe for state changes. Please see the examples section on how to configure it.<br/>
**default (on of [rising, falling, switch, motion]**: The default edge that is applied when not configured. Please see the examples section for further details.

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

**host (str)**: Url to your `home assistant` instance (e.g. http://my-hass:8123)<br/>
**token (str)**: Your long lived access token to access the websocket api. See below for further instructions<br/>
**include (str or list[str])**: Patterns of entity state changes to include. All state changes that do not match the
defined patterns will be ignored</br>
**exclude (str or list[str]**:Patterns of entity state changes to exclude. All state changes that do match the defined
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

**port (int, optional)**: The port the rest server should listen to for requests. Default is 5000.<br/>
**allowed_methods (str or list, optional)**: List of http methods that are allowed. Default is 'GET'.<br/>
**server_impl (str, optional)**: Choose the implementation of the WSGI-Server (wraps the flask-app).
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
	'cpu_freq': 700,  # in Mhz
	'cpu_use': 6.6,  # in %
	'cpu_temp': 52.6,  # in °C (might not be available on all systems, e.g. MacOS)
	'memory_use': 56.0,  # in %
	'swap_use': 23.2,  # in %
	'disk_use': 69.8,  # in %  (of your root)
	'load_1m': 1.81591796875,  # CPU queue length last minute
	'load_5m': 2.06689453125,  # CPU queue length last 5 minutes
	'load_15m': 2.15478515625  # CPU queue length last 15 minutes
}
```

__Examples__

```yaml
- name: stats
  pull:
    plugin: pnp.plugins.pull.monitor.Stats
    args:
      interval: 10s
      instant_run: True
  push:
    plugin: pnp.plugins.push.simple.Echo
```
## pnp.plugins.pull.mqtt.Subscribe

Pulls messages from the specified topic from the given mosquitto mqtt broker (identified by host and port).

__Arguments__

**host (str)**: Host where the mosquitto broker is running.<br/>
**port (int)**: Port where the mosquitto broker is listening.<br/>
**topic (str)**: Topic to pull messages from.
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

## pnp.plugins.pull.sensor.DHT

Periodically polls a dht11 or dht22 (aka am2302) for temperature and humidity readings.
Polling interval is controlled by `interval`.

Requires extra `dht`.

__Arguments__

**device (str, optional)**: The device to poll (one of dht22, dht11, am2302). Default is 'dht22'.<br/>
**data_gpio (int, optional)**: The data gpio port where the device operates on. Default is 17.</br>
**humidity_offset (float, optional)**: Positive/Negative offset for humidity. Default is 0.0.</br>
**temp_offset (float, optional)**: Positive/Negative offset for temperature. Default is 0.0.

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
      instant_run: True
  push:
    - plugin: pnp.plugins.push.simple.Echo
      selector: payload.temperature  # Temperature reading
    - plugin: pnp.plugins.push.simple.Echo
      selector: payload.humidity  # Humidity reading
```
## pnp.plugins.pull.sensor.OpenWeather

Periodically polls weather data from the `OpenWeatherMap` api.

__Arguments__

**api_key (str):** The api_key you got from OpenWeatherMap after registration.<br/>
**lat (float):** Latitude. If you pass `lat`, you have to pass `lon` as well.<br/>
**lon (float):** Longitude. If you pass `lon`, you have to pass `lat` as well.<br/>
**city_name (str):** The name of your city. To minimize ambiguity use lat/lon or your country as a suffix,
e.g. London,GB.<br/>
**units (str on of (metric, imperial, kelvin))**: Specify units for temperature and speed.<br/>
imperial = fahrenheit + miles/hour, metric = celsius + m/secs, kelvin = kelvin + m/secs. Default is metric.<br/>
**tz (str, optional)**: Time zone to use for current time and last updated time. Default is your local timezone.

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
## Make sure you export your api key with: `export OPENWEATHER_API_KEY=<your_api_key>`

- name: openweather
  pull:
    plugin: pnp.plugins.pull.sensor.OpenWeather
    args:
      city_name: "Hamburg,DE"  # Alternative: pass lat and lon
      # lon: 10
      # lat: 53.55
      units: metric  # imperial (fahrenheit + miles/hour), metric (celsius + m/secs), kelvin (kelvin + m/secs)
      instant_run: True
      # tz: GMT
  push:
    plugin: pnp.plugins.push.simple.Echo
```
## pnp.plugins.pull.sensor.Sound

Listens to the microphone in realtime and searches the stream for a specific sound pattern.
Practical example: I use this plugin to recognize my doorbell without tampering with the electrical device ;-)

Requires extra `sound`.

__Arguments__

**wav_file (str/filepath)**: The file that contains the original sound pattern to listen for.<br/>
**device_index (int, optional)**: The index of the microphone device. Run `pnp_record_sound --list` to get the index.
If not specified pyAudio will try to find a capable device.</br>
**mode (Union[pearson,std], optional)**: Correlation/similarity method. Default is pearson.</br>
**sensitivity_offset (float, optional)**: Adjusts sensitivity for similarity.
Positive means less sensitive; negative is more sensitive. You should try out 0.1 steps. Default is 0.0.<br/>
**cool_down (duration literal, optional)**: Prevents the pull to emit more than one sound detection event per
cool down duration. Default is 10 seconds.

Hints:
* You can list your available input devices: `pnp_record_sound --list`
* You can record a wav file from an input device: `pnp_record_sound <out.wav> <seconds_to_record> --index=<idx>`


__Result__

Will only emit the event below when the correlation coefficient is above or equal the threshold.

```yaml
{
    "data": ding,  # Name of the wav_file without path and extension
    "corrcoef": 0.82,  # Correlation coefficient probably between [-1;+1] for pearson
    "threshold": 0.6  # Threshold influenced by sensitivity_offset
}
```

__Examples__

```yaml
- name: sound_detector
  pull:
    plugin: pnp.plugins.pull.sensor.Sound
    args:
      wav_file: doorbell.wav  # The file to compare for similarity
      device_index: # The index of the microphone devices. If not specified pyAudio will try to find a capable device
      mode: pearson  # Use pearson correlation coefficient [pearson, std]
      sensitivity_offset: 0.1  # Adjust sensitivity. Positive means less sensitive; negative is more sensitive
      cool_down: 3s  # Prevents the pull to emit more than one sound detection event every 3 seconds
  push:
    - plugin: pnp.plugins.push.simple.Echo

```

__Docker__

To use a microphone the docker container needs more permissions:

```
docker run -ti --rm \
    --device /dev/snd:/dev/snd:r \
    --privileged \
    --cap-add=SYS_RAWIO
    hazard/pnp
```
## pnp.plugins.pull.simple.Count

Emits every `wait` seconds a counting value which runs from `from_cnt` to `to_cnt`.
If `to_cnt` is None the counter will count to infinity.

__Arguments__

**wait (int)**: Wait the amount of seconds before emitting the next counter.<br/>
**from_cnt (int)**: Starting value of the counter.<br/>
**to_cnt (int, optional)**: End value of the counter. If not passed set to "infinity" (precise: int.max).

__Result__

Counter value (int).

__Examples__

```yaml
- name: count
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 1
      from_cnt: 1
      to_cnt: 10
  push:
    plugin: pnp.plugins.push.simple.Echo
```
## pnp.plugins.pull.simple.Repeat

Emits every `wait` seconds the same `repeat`.

__Arguments__

**wait (int)**: Wait the amount of seconds before emitting the next repeat.<br/>
**repeat (any)**: The object to emit.

__Result__

Emits the `repeat`-object as it is.

__Examples__

```yaml
- name: repeat
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      repeat: "Hello World"  # Repeats 'Hello World'
      wait: 1  # Every second
  push:
    plugin: pnp.plugins.push.simple.Echo
```
## pnp.plugins.pull.zway.ZwayPoll

Pulls the specified json content from the zway rest api. The content is specified by the url, e.g.
`http://<host>:8083/ZWaveAPI/Run/devices` will pull all devices and serve the result as a json.

Specify the polling interval by setting the argument `interval`. User / password combination is required when
your api is protected against guest access (by default it is).

Use multiple pushes and the related selectors to extract the required content like temperature readings (see
the examples section for guidance).

__Arguments__

**url (str)**: The url to poll periodically.<br/>
**user (str)**: Authentication user name.<br/>
**password (str)**: Authentication password.<br/>
**interval (polling literal, optional)**: Polling interval (default: 1m).

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

**Fibaro Motion Sensor**
* Temperature
`payload[deviceid].instances[0].commandClasses[49].data[1].val.value`
* Luminescence
`payload[deviceid].instances[0].commandClasses[49].data[3].val.value`

**fibaro Wallplug**
* Meter
`payload[deviceid].instances[0].commandClasses[50].data[0].val.value`

**Thermostat (Danfoss / other should work as well)**
* Setpoint
`payload[deviceid].instances[0].commandClasses[67].data[1].val.value`

**Battery operated devices**
* Battery level
`payload[deviceid].instances[0].commandClasses[128].data.last.value`

## pnp.plugins.pull.zway.ZwayReceiver

Setups a http server to process incoming GET-requests from the Zway-App [`HttpGet`](https://github.com/hplato/Zway-HTTPGet/blob/master/index.js).

__Arguments__

**url_format (str)**: The url_format that is configured in your HttpGet App. If you configured
`http://<ip>:<port>/set?device=%DEVICE%&state=%VALUE%` (default of the App), you basically have to copy the path
component `set?device=%DEVICE%&state=%VALUE%` to be your `url_format`.<br/>
**mode ([mapping, auto, both])**: If set to `mapping` (default) you should provide the `device_mapping` to manually map your virtual devices.
If set to `auto` the plugin will try to determine the device_id, command class, mode and the type on it's own. If set to `both` the plugin
will first try the `device_mapping` and then perform the auto-magic.</br>
**device_mapping (Or(Dict[Str, Str], Dict[Str, Dict]), optional)**: A mapping to map the somewhat cryptic virtual device names to
human readable ones. Default is None, which means that no mapping will be performed. Two ways possible:
1. Ordinary mapping from virtual device name -> alias.
2. Enhanced mapping from virtual device name to dictionary with additional properties. One property has to be alias.<br/>
**ignore_unknown_devices (bool, optional)**: If set to True all incoming requests that are associated with an device
that is not part of the mapping or - when mode = [auto, both] - cannot be auto mapped will be ignored. Default is False.<br/>

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
      ignore_unknown_devices: False
  push:
    - plugin: pnp.plugins.push.simple.Echo
      selector: "'Got value {} from device {} ({}) with props {}'.format(data.value, data.device_name, data.raw_device, data.props)"
```

## pnp.plugins.push.fs.FileDump

This push dumps the given `payload` to a file to the specified `directory`.
If argument `file_name` is None, a name will be generated based on the current datetime (%Y%m%d-%H%M%S).
If `file_name` is not passed (or None) you should pass `extension` to specify the extension of the generated
file name.
Argument `binary_mode` controls whether the dump is binary (mode=wb) or text (mode=w).

__Arguments__

**directory (str, optional)**: The target directory to store the dumps. Default is '.' (current directory).<br/>
**file_name (str, optional)**: The name of the file to dump. If set to None a file name will be automatically
    generated. You can specify the file_name via the envelope, too. Envelope will override __init__ file name.
    Default is None.<br/>
**extension (str, optional)**: The extension to use when the file name is automatically generated. Can be overridden by
    envelope. Default is '.dump'.<br/>
**binary_mode (bool, optional)**: If set to True the file will be written in binary mode ('wb');
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
      directory: "/tmp"
      file_name: null  # Auto-generated file (timestamp)
      extension: ".txt"  # Extension of auto-generated file
      binary_mode: False  # text mode
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
      directory: "/tmp"
      file_name: null  # Auto-generated file (timestamp)
      extension: ".txt"  # Extension of auto-generated file
      binary_mode: False  # text mode
    deps:
      - plugin: pnp.plugins.push.simple.Echo
```
## pnp.plugins.push.http.Call

Makes a request to a http resource.

__Arguments__

**url (str)**: Request url. Can be overridden via envelope.<br/>
**method (str, optional)**: The http method to use for the request. Must be a valid http method (GET, POST, ...).
    Default is 'GET'. Can be overridden via envelope.<br/>
**fail_on_error (bool, optional)**: If True the push will fail on a http status code <> 2xx. This leads to an error
    message recorded into the logs and no further execution of any dependencies. Default is False. Can be overridden
    by the envelope.<br/>
**provide_response (bool, optional)**: If True the push will _not_ return the payload as it is, but instead provide the
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
      wait: 5
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
      wait: 5
  push:
    plugin: pnp.plugins.push.http.Call
    args:
      url: http://localhost:5000/
      provide_response: True
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

**token_file (str)**: The file that contains your tokens. See below for further details<br/>
**recipient (str or List[str])**: The recipient (to) of the e-mail. Optionally you can pass a list for multiple recipients.
    Can be overridden via envelope.<br/>
**subject (str, optional)**: Sets the subject of the e-mail. Default is None, which means the subject is expected
    to be set by the envelope. Can be overridden by the envelope.<br/>
**sender (str, optional)**: Sets the sender of the e-mail. Default is 'pnp'. Can be overridden by the envelope.<br/>
**attachment (str, optional)**: Can be set by the envelope. If set the `attachment` should point to a valid file to
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
      ignore_directories: True
      events:
        - created
      load_file: False
  push:
    plugin: pnp.plugins.push.mail.GMail
    selector:
      subject: "lambda p: basename(p.source)"  # basename(p.source) = file name
      data: # Message body -> None -> Just the attachment
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

__Arguments__

**known_faces (dict<str, file_path as str>, optional)**: Mapping of a person's name to a list of images that contain
    the person's face. Default is None.<br/>
**known_faces_dir (str, optional)**: A directory containing images with known persons (file_name -> person's name).
    Default is None.<br/>
**unknown_label (str, optional)**: Tag label of unknown faces. Default is 'Unknown'.

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
      recursive: True
      patterns: "*.jpg"
      ignore_directories: True
      case_sensitive: False
      events: [created]
      load_file: True
      mode: binary
      base64: False
  push:
    plugin: pnp.plugins.push.ml.FaceR
    args:
      known_faces_dir: "/tmp/faces"
      unknown_label: "don't know him"
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
      instant_run: True
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
      instant_run: True
      interval: 5m
  push:
    - plugin: pnp.plugins.push.mqtt.Discovery
      selector:
        data: "lambda data: data.get('battery_level')"
        object_id: "lambda data: 'fb_{}_battery'.format(data.get('device_version', '').replace(' ', '_').lower())"
      unwrap: True
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
      unwrap: True
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

**host (str)**: The host where the mosquitto broker is running.<br/>
**port (int, optional)**: The port where the mosquitto broker is listening. Default is 1883.<br/>
**topic (str, optional)**: The topic to subscribe to. If set to None the envelope of the
    payload has to contain a 'topic' key or the push will fail (default is None). If both exists
    the topic from the envelope will overrule the __init__ one.<br/>
**retain (bool, optional)**: If set to True will mark the message as retained. Default is False.
    See the mosquitto man page for further guidance
    [https://mosquitto.org/man/mqtt-7.html](https://mosquitto.org/man/mqtt-7.html).<br/>
**multi (bool, optional)**: If set to True the payload is expected to be a dictionary. Each item of that dictionary will
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
      retain: True
```

```yaml
- name: mqtt
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 1
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
      instant_run: True
      interval: 10s
  push:
    # Push them to the mqtt
    plugin: pnp.plugins.push.mqtt.Publish
    args:
      host: localhost
      topic: devices/localhost/
      port: 1883
      retain: True
      # Each item of the payload-dict (cpu_count, cpu_usage, ...) will be pushed to the broker as multiple items.
      # The key of the item will be appended to the topic, e.g. `devices/localhost/cpu_count`.
      # The value of the item is the actual payload.
      multi: True
```
## pnp.plugins.push.notify.Pushbullet

Sends a message to the [Pushbullet](http://www.pushbullet.com) service.
The type of the message will guessed:

* `push_link` for a single http link
* `push_file` if the link is directed to a file (mimetype will be guessed)
* `push_note` for everything else (converted to `str`)

Requires extra `pushbullet`.

__Arguments__

**api_key (str)**: The api key to your pushbullet account.<br/>
**title (str, optional)**: The title to use for your messages. Defaults to `pnp`</br>

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
      ignore_directories: True
      events:
        - created
      load_file: False
  push:
    plugin: pnp.plugins.push.notify.Pushbullet
    args:
      title: "Watcher"
    selector: "'New file: {}'.format(data.source)"

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
      wait: 1
      from_cnt: 1
      to_cnt: 10
  push:
    plugin: pnp.plugins.push.simple.Echo
```
## pnp.plugins.push.simple.Execute

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
## pnp.plugins.push.storage.Dropbox

Uploads provided file to the specified dropbox account.

__Arguments__

**api_key (str)**: The api key to your dropbox account/app.<br/>
**target_file_name (str, optional)**: The file path on the server where to upload the file to.
If not specified you have to specify this argument during push time by setting it in the envelope.<br/>
**create_shared_link (bool, optional)**: If set to True, the push will create a publicly available link to your uploaded file. Default is `True`.

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
      ignore_directories: True
      events:
        - created
        - modified
      load_file: False
  push:
    - plugin: pnp.plugins.push.storage.Dropbox
      args:
        create_shared_link: True  # Create a publicly available link
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

**host (str)**: The host where the influxdb is running.<br/>
**port (int)**: The port where the influxdb service is listening on.<br/>
**user (str)**: Username to use for authentication.<br/>
**password (str)**: Related password.<br/>
**database (str)**: The database to write to.<br/>
**protocol (str)**: Line protocol template (augmented with payload-data).

All arguments can be automatically injected via environment variables with `INFLUX` prefix (e.g. `INFLUX_HOST`).

__Result__

For the ability to chain multiple pushes together the payload is simply returned as is.

__Examples__

```yaml
- name: mqtt_pull
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

## pnp.plugins.udf.hass.State

Fetches the state of an entity from home assistant by a rest-api request.

__Arguments__

**url (str)**: The url to your home assistant instance (e.g. http://hass:8123)<br/>
**token (str)**: The love live access token to get access to home assistant<br/>
**timeout (Optional[int])**: Tell the request to stop waiting for a reponse after given number of seconds. Default is 5 seconds.

__Call Arguments__

**entity_id (str)**: The entity to fetch the state<br>
**attribute (Optional[str])**: Optionally you can fetch the state of one of the entities attributes.
Default is None (which means to fetch the state of the entity)

__Result__

Returns the current state of the entity or one of it's attributes. If the entity is not known to home assistant an exception is raised.
In case of an attribute does not exists, None will be returned instead to signal it's absence.

__Examples__

```yaml
udfs:
  # Defines the udf. name is the actual alias you can call in selector expressions.
  - name: hass_state
    plugin: pnp.plugins.udf.hass.State
    args:
      url: http://localhost:8123
      token: "{{env::HA_TOKEN}}"
tasks:
  - name: hass_state
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        repeat: "Hello World"  # Repeats 'Hello World'
        wait: 1  # Every second
    push:
      - plugin: pnp.plugins.push.simple.Echo
        # Will only print the data when attribute azimuth of the sun component is above 200
        selector: "'azimuth is greater than 200' if hass_state('sun.sun', attribute='azimuth') > 200.0 else SUPPRESS"
      - plugin: pnp.plugins.push.simple.Echo
        # Will only print the data when the state of the sun component is above 'above_horizon'
        selector: "'above_horizon' if hass_state('sun.sun') == 'above_horizon' else SUPPRESS"
```
## pnp.plugins.udf.simple.Counter

Memories a counter value which is increased everytime you call the udf.

__Arguments__

**init (Optional[int])**: The initialization value of the counter. Default is 0.

__Result__

Returns the current counter.

__Examples__

```yaml
udfs:
  # Defines the udf. name is the actual alias you can call in selector expressions.
  - name: counter
    plugin: pnp.plugins.udf.simple.Counter
    args:
      init: 1
tasks:
  - name: countme
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        repeat: "Hello World"  # Repeats 'Hello World'
        wait: 1  # Every second
    push:
      - plugin: pnp.plugins.push.simple.Echo
        selector:
          data: "lambda data: data"
          count: "lambda data: counter()"  # Calls the udf
```
## pnp.plugins.udf.simple.Memory

Returns a previously memorized value when called.

__Arguments__

**init (any, optional)**: The initial memory of the plugin. Default is None.

__Call Arguments__

**new_memory (any, optional)**: After emitting the current memorized value the current memory is overwritten by this value.
Will only be overwritten if the parameter is specified.

__Result__

Returns the memorized value.

__Examples__

```yaml
udfs:
  - name: mem
    plugin: pnp.plugins.udf.simple.Memory
    args:
      init: 1
tasks:
  - name: countme
    pull:
      plugin: pnp.plugins.pull.simple.Count
      args:
        from_cnt: 1
        wait: 1  # Every second
    push:
      - plugin: pnp.plugins.push.simple.Echo
        # Will memorize every uneven count
        selector: "mem() if data % 2 == 0 else mem(new_memory=data)"
```
