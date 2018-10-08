# Pull 'n' Push

[![Build Status](https://travis-ci.org/HazardDede/pnp.svg?branch=master)](https://travis-ci.org/HazardDede/pnp)

Pulls data from sources and pushes it to sinks.

1\.  [Installation](#installation)  
2\.  [Getting started](#gettingstarted)  
3\.  [Building Blocks](#buildingblocks)  
3.1\.  [Pull](#pull)  
3.2\.  [Push](#push)  
3.3\.  [Selector](#selector)  
3.4\.  [Dependencies](#dependencies)  
3.5\.  [Envelope (>= 0.7.1)](#envelope>=0.7.1)  
3.6\.  [Engines (>= 0.10.0)](#engines>=0.10.0)  
3.6.1\.  [pnp.engines.sequential.SequentialEngine](#pnp.engines.sequential.sequentialengine)  
3.6.2\.  [pnp.engines.thread.ThreadEngine](#pnp.engines.thread.threadengine)  
3.6.3\.  [pnp.engines.process.ProcessEngine](#pnp.engines.process.processengine)  
4\.  [Useful hints](#usefulhints)  
4.1\.  [Configuration checking](#configurationchecking)  
4.2\.  [Logging (>= 0.11.0)](#logging>=0.11.0)  
4.3\.  [dictmentor (>= 0.11.0)](#dictmentor>=0.11.0)  
4.4\.  [Docker images](#dockerimages)  
5\.  [Plugins](#plugins)  
5.1\.  [pnp.plugins.pull.simple.Count](#pnp.plugins.pull.simple.count)  
5.2\.  [pnp.plugins.pull.sensor.DHT](#pnp.plugins.pull.sensor.dht)  
5.3\.  [pnp.plugins.pull.fs.FileSystemWatcher](#pnp.plugins.pull.fs.filesystemwatcher)  
5.4\.  [pnp.plugins.pull.mqtt.MQTTPull](#pnp.plugins.pull.mqtt.mqttpull)  
5.5\.  [pnp.plugins.pull.simple.Repeat](#pnp.plugins.pull.simple.repeat)  
5.6\.  [pnp.plugins.pull.http.Server](#pnp.plugins.pull.http.server)  
5.7\.  [pnp.plugins.pull.ZwayPoll](#pnp.plugins.pull.zwaypoll)  
5.8\.  [pnp.plugins.pull.ZwayReceiver](#pnp.plugins.pull.zwayreceiver)  
5.9\.  [pnp.plugins.push.simple.Echo](#pnp.plugins.push.simple.echo)  
5.10\.  [pnp.plugins.push.ml.FaceR](#pnp.plugins.push.ml.facer)  
5.11\.  [pnp.plugins.push.fs.FileDump](#pnp.plugins.push.fs.filedump)  
5.12\.  [pnp.plugins.push.http.Call](#pnp.plugins.push.http.call)  
5.13\.  [pnp.plugins.push.timedb.InfluxPush](#pnp.plugins.push.timedb.influxpush)  
5.14\.  [pnp.plugins.push.mqtt.MQTTPush](#pnp.plugins.push.mqtt.mqttpush)  
6\.  [Changelog](#changelog)  

<a name="installation"></a>

## 1\. Installation

    pip install pnp

Optional extras

* dht: Enables `pnp.plugins.pull.sensor.DHT` (temperature and humidity sensor). Only works on ARM-based systems (like raspberry, arduino)
* fswatcher: Enables `pnp.plugins.pull.fs.FileSystemWatcher` (Watch file system for created, modified, 
deleted, moved files)
* faceR: Enables `pnp.plugins.push.ml.FaceR` (Screen image files for known faces)

Installation with extras:
    
    pip install pnp[fswatcher,faceR]
    # In case of extra 'dht' you have to enable the option --process-dependency-links ...
    # ... cause the required adafruit package is not on pypi.
    pip install --process-dependency-links pnp[dht]


<a name="gettingstarted"></a>

## 2\. Getting started

Define `pulls` to suck/pull data from source systems.
Define one `push` or multiple `pushes` per pull to transfer the pulled data anywhere else (you only need a plugin that 
knows how to handle the target). You can define your configurations in `yaml` or `json`. 
It is up to you. I prefer yaml...

```yaml
- name: hello-world
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      wait: 1
      repeat: "Hello World"
  push:
    - plugin: pnp.plugins.push.simple.Echo
```
        
Copy this configuration and create the file `helloworld.yaml`. Run it:

    pnp helloworld.yaml

This example yields the string 'Hello World' every second.

Tip: You can validate your config without actually executing it with

```yaml
   pnp --check helloworld.yaml
```

<a name="buildingblocks"></a>

## 3\. Building Blocks

Below the basic building blocks of pull 'n' push are explained in more detail


<a name="pull"></a>

### 3.1\. Pull

As stated before pulls fetch data from various source systems and/or apis. Please see the section plugins for already
implemented pulls. To instantiate a pull by configuration file you only have to provide it's fully qualified name
and the argument that should be passed.

```yaml
- name: example
  pull:
    plugin: pnp.plugins.pull.mqtt.MQTTPull
    args:
      host: localhost
      port: 1883
      topic: test/#

```
        
The above snippet will create a pull that listens on the topic test/# on a mqtt broker. The output of the pull
is a dictionary that contains the topic, levels and the actual payload.

    # When the message 'Here i am' arrives on the topic 'test/foo/bar' then the output will look like that:
    {'topic': 'test/foo/bar', 'levels': ['test', 'foo', 'bar'], 'payload': 'Here i am'}


<a name="push"></a>

### 3.2\. Push

A pull passes its data to multiple pushes to transfer/transform the data. For example a push might save sensor data
to influx or dump a file to the file system.

```yaml
- name: example
  pull:
    plugin: pnp.plugins.pull.mqtt.MQTTPull
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    - plugin: pnp.plugins.push.fs.FileDump
      args:
        directory: "/tmp"
        binary_mode: False
    - plugin: pnp.plugins.push.simple.Echo
```
      
The above snippet adds two pushes to the already known pull. The first push takes the incoming data and dumps it into
the specified directory as a textfile. The second push just prints out the incoming data.


<a name="selector"></a>

### 3.3\. Selector

Sometimes the output of a pull needs to be transformed before the specified push can handle it. `Selectors` to the 
rescue. Given our input we decide to just dump the payload and print out the first level of the topic.

```yaml
- name: example
  pull:
    plugin: pnp.plugins.pull.mqtt.MQTTPull
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    - plugin: pnp.plugins.push.fs.FileDump
      selector: data.payload
      args:
        directory: "/tmp"
        binary_mode: False
    - plugin: pnp.plugins.push.simple.Echo
      selector: data.levels[0]
```

Easy as that. We can reference our incoming data via `data` or `payload`.


<a name="dependencies"></a>

### 3.4\. Dependencies

By default any pushes will execute in parallel (not completly true) when new incoming data is available.
But now it would be nice if we could chain pushes together. So that the output if one push becomes the 
input of the next push. The good thing is: Yes we can.

Back to our example let's assume we want to print out the path to the created file dump after the dump is created.

```yaml
- name: example
  pull:
    plugin: pnp.plugins.pull.mqtt.MQTTPull
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    - plugin: pnp.plugins.push.fs.FileDump
      selector: data.payload
      args:
        directory: "/tmp"
        binary_mode: False
      deps:
        - plugin: pnp.plugins.push.simple.Echo
    - plugin: pnp.plugins.push.simple.Echo
      selector: data.levels[0]
```
        
As you can see we just add a dependant push to the previous one.


<a name="envelope>=0.7.1"></a>

### 3.5\. Envelope (>= 0.7.1)

Using envelopes it is possible to change the behaviour of `pushes` during runtime.
Best examples are the `pnp.plugins.push.fs.FileDump` and `pnp.plugins.push.mqtt.MQTTPush` plugins, where
you can override / set the actual `file_name` and `extension` of the file to dump 
resp. the `topic` where the message should be published.

Given the example ...

```yaml
- name: envelope
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 1
  push:
    plugin: pnp.plugins.push.fs.FileDump
    selector: '{"file_name": str(data), "extension": ".cnt", "data": data}'
    args:
      directory: "/tmp/counter"
      file_name: "counter"  # Overridden by envelope
      extension: ".txt"  #  Overridden by envelope
      binary_mode: False  # text mode

```
          
... this push dumps multiple files (0.cnt, 1.cnt, 2.cnt, ...) for each pulled counter value,
instead of dumping one file 'couter.txt' which is overridden each time a new counter is emitted.

How does this work: If the emitted or transformed payload (via selector) contains the key `data` or
`payload` it is assumed that the actual payload is the data stored in this key and all other keys
represent the so called `envelope`.

Remark: This feature might actually break your existing configurations if you use the plugin
`pnp.plugins.pull.mqtt.MQTTPull` which will now emit an enveloped payload.

This snippet echoed a dictionary with the keys 'topic', 'levels' and 'payload' previously to version 0.7.2.
It will now differentiate between the actual 'payload' (key 'payload' resp. 'data') and the envelope (other keys).

    - name: subscriber
      pull:
        plugin: pnp.plugins.pull.mqtt.MQTTPull
        args:
          host: localhost
          topic: test/counter
      push:
        plugin: pnp.plugins.push.simple.Echo
        
If you want to "restore" the previous behaviour, you only have to wrap the whole payload
into a dictionary inside the 'payload' or 'data' key via selector.

    - name: subscriber
      pull:
        plugin: pnp.plugins.pull.mqtt.MQTTPull
        args:
          host: localhost
          topic: test/counter
      push:
        plugin: pnp.plugins.push.simple.Echo
        selector: "{'data': data}"


<a name="engines>=0.10.0"></a>

### 3.6\. Engines (>= 0.10.0)

If you do not specify any engine the `ThreadEngine` is chosen by default accompanied by the `AdvancedRetryHandler`.
This keeps maximum backwards compatibility.

<a name="pnp.engines.sequential.sequentialengine"></a>

#### 3.6.1\. pnp.engines.sequential.SequentialEngine

By using the `Sequential` engine you can run your configs as scripts. Given the example below, the "script" will
end when it has finished counting to 3. Make sure to use the `NoRetryHandler` to actually end the runner when
the pull has finished instead of retrying the "failed" `pull`. You cn only run a single task not multiple.
When you want to run multiple task in a concurrent manner you have to use the `ThreadEngine` or the `ProcessEngine`.

```yaml
#### Simple sequential handler
#### Counts from 1 to 3 and then terminates
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

<a name="pnp.engines.thread.threadengine"></a>

#### 3.6.2\. pnp.engines.thread.ThreadEngine

```yaml
#### Will use threads to accomplish concurrency
#### Drawback: If a plugin does not stop gracefully the termination will hang...
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

<a name="pnp.engines.process.processengine"></a>

#### 3.6.3\. pnp.engines.process.ProcessEngine

```yaml
#### Will use multiprocessing to accomplish concurrency
#### Drawback: Some plugins might not work or need to be aware of
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

<a name="usefulhints"></a>

## 4\. Useful hints

<a name="configurationchecking"></a>

### 4.1\. Configuration checking

You can check your pnp configuration file by starting pnp with the `-c | --check` flag set. This will only run
the initializer but not execute the configuration.

```bash
pnp --check <pnp_configuration>
```

<a name="logging>=0.11.0"></a>

### 4.2\. Logging (>= 0.11.0)

You can use different logging configurations in two ways:

```bash
# Specify when starting pnp
pnp --log=<logging_configuration> <pnp_configuration>
# Specify by environment variable
export PNP_LOG_CONF=<logging_configuration>
pnp <pnp_configuration>
```

A simple logging configuration that will log severe errors to a separate rotating log file looks like this:

```yaml
version: 1
disable_existing_loggers: False

formatters:
    simple:
        format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

handlers:
    console:
        class: logging.StreamHandler
        level: DEBUG
        formatter: simple
        stream: ext://sys.stdout

    error_file_handler:
        class: logging.handlers.RotatingFileHandler
        level: ERROR
        formatter: simple
        filename: errors.log
        maxBytes: 10485760 # 10MB
        backupCount: 20
        encoding: utf8

root:
    level: INFO
    handlers: [console, error_file_handler]
```


<a name="dictmentor>=0.11.0"></a>

### 4.3\. dictmentor (>= 0.11.0)

You can augment the configuration by extensions from the `dictmentor` package.
Please see [DictMentor](https://github.com/HazardDede/dictmentor) for further reference.

The `DictMentor` instance will be instantiated with the following code and thus the following extensions:

```yaml
from dictmentor import DictMentor, ext
return DictMentor(
    ext.Environment(fail_on_unset=True),
    ext.ExternalResource(base_path=os.path.dirname(config_path)),
    ext.ExternalYamlResource(base_path=os.path.dirname(config_path))
)
```

Example:

```yaml
# Uses the dictmentor package to augment the configuration by dictmentor extensions.
# Make sure to export the environment variable to echo:
# export MESSAGE="Hello World"

- name: dictmentor
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      wait: 1
      repeat: "{{env::MESSAGE}}"
  push:
    - external: echo.pull
    - external: nop.pull
```

```yaml
# Contents of echo.pull
plugin: pnp.plugins.push.simple.Echo
```

```yaml
# Contents of nop.pull
plugin: pnp.plugins.push.simple.Nop
```


<a name="dockerimages"></a>

### 4.4\. Docker images

```bash
make docker  # OR: make docker-arm  for raspberry image
# Mount the task and logging configuration when starting up the container
docker run -it --rm \
    -v /path/to/pnp/config/01_hello_world.yaml:/config/config.yaml \
    -v /path/to/logging/config/file.logging:/config/logging.yaml \
    pnp:0.10.0
```


<a name="plugins"></a>

## 5\. Plugins

<a name="pnp.plugins.pull.simple.count"></a>

### 5.1\. pnp.plugins.pull.simple.Count

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
<a name="pnp.plugins.pull.sensor.dht"></a>

### 5.2\. pnp.plugins.pull.sensor.DHT

Periodically polls a dht11 or dht22 (aka am2302) for temperature and humidity readings.
Polling interval is controlled by `interval`.

__Arguments__

**device (str, optional)**: The device to poll (one of dht22, dht11, am2302). Default is 'dht22'.<br/>
**data_gpio (int, optional)**: The data gpio port where the device operates on. Default is 17.

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
  push:
    - plugin: pnp.plugins.push.simple.Echo
      selector: payload.temperature  # Temperature reading
    - plugin: pnp.plugins.push.simple.Echo
      selector: payload.humidity  # Humidity reading
```
<a name="pnp.plugins.pull.fs.filesystemwatcher"></a>

### 5.3\. pnp.plugins.pull.fs.FileSystemWatcher

Watches the given directory for changes like created, moved, modified and deleted files. If `ignore_directories` is
set to False, then directories will be reported as well.

Per default will recursively report any file that is touched, changed or deleted in the given path. The
directory itself or subdirectories will be object to reporting too, if `ignore_directories` is set to False.

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
<a name="pnp.plugins.pull.mqtt.mqttpull"></a>

### 5.4\. pnp.plugins.pull.mqtt.MQTTPull

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
    plugin: pnp.plugins.pull.mqtt.MQTTPull
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    plugin: pnp.plugins.push.simple.Echo
```

<a name="pnp.plugins.pull.simple.repeat"></a>

### 5.5\. pnp.plugins.pull.simple.Repeat

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
<a name="pnp.plugins.pull.http.server"></a>

### 5.6\. pnp.plugins.pull.http.Server

Listens on the specified `port` for requests to any endpoint.
Any data passed to the endpoint will be tried to be parsed to a dictionary (json). If this is not possible
the data will be passed as is. See sections `Result` for specific payload and examples.

Remark: You will not able to make requests to the endpoint DELETE `/_shutdown` because it is used internally.

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
<a name="pnp.plugins.pull.zwaypoll"></a>

### 5.7\. pnp.plugins.pull.ZwayPoll

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
### Please make sure to adjust url and device ids
### Username and Password are injected from environment variables:
###     export ZWAY_USER=admin
###     export ZWAY_PASSWORD=secret_one
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

<a name="pnp.plugins.pull.zwayreceiver"></a>

### 5.8\. pnp.plugins.pull.ZwayReceiver

Setups a http server to process incoming GET-requests from the Zway-App [`HttpGet`](https://github.com/hplato/Zway-HTTPGet/blob/master/index.js).

__Arguments__

**url_format (str)**: The url_format that is configured in your HttpGet App. If you configured
`http://<ip>:<port>/set?device=%DEVICE%&state=%VALUE%` (default of the App), you basically have to copy the path
component `set?device=%DEVICE%&state=%VALUE%` to be your `url_format`.<br/>
**device_mapping (Or(Dict[Str, Str], Dict[Str, Dict]), optional)**: A mapping to map the somewhat cryptic virtual device names to
human readable ones. Default is None, which means that no mapping will be performed. Two ways possible:
1. Ordinary mapping from virtual device name -> alias.
2. Enhanced mapping from virtual device name to dictionary with additional properties. One property has to be alias.<br/>
**ignore_unknown_devices (bool, optional)**: If set to True all incoming requests that are associated with an device
that is not part of the mapping will be ignored. Default is False.<br/>

Additionally the component will accept any arguments that `pnp.plugins.pull.http.Server` would accept.

__Result__

Given the url_format `%DEVICE%?value=%VALUE%`, the url `http://<ip>:<port>/set?vdevice1?value=5.5` and
the device_mapping `vdevice1 -> alias of vdevice1` the emitted message will look like this:

```yaml
{
    'device_name': 'alias of vdevice1',
    'raw_device': 'vdevice1'
    'value': 5.5,
    'props': {}
}
```

__Examples__

```yaml
- name: zway_receiver
  pull:
    plugin: pnp.plugins.pull.zway.ZwayReceiver
    args:
      port: 5000
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

<a name="pnp.plugins.push.simple.echo"></a>

### 5.9\. pnp.plugins.push.simple.Echo

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
<a name="pnp.plugins.push.ml.facer"></a>

### 5.10\. pnp.plugins.push.ml.FaceR

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
<a name="pnp.plugins.push.fs.filedump"></a>

### 5.11\. pnp.plugins.push.fs.FileDump

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
    selector: '{"payload": payload, "file_name": "hello-world", "extension": ".hello"}'
    args:
      directory: "/tmp"
      file_name: null  # Auto-generated file (timestamp)
      extension: ".txt"  # Extension of auto-generated file
      binary_mode: False  # text mode
    deps:
      - plugin: pnp.plugins.push.simple.Echo
```
<a name="pnp.plugins.push.http.call"></a>

### 5.12\. pnp.plugins.push.http.Call

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
### Simple example calling the built-in rest server
### Oscillates between http method GET and POST. Depending on the fact if the counter is even or not.
- name: http_call
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 5
  push:
    plugin: pnp.plugins.push.http.Call
    selector: "dict(data=dict(counter=payload), method='POST' if int(payload) % 2 == 0 else 'GET')"
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
### Demonstrates the use of `provide_response` set to True.
### Call will return a response object to dependent push instances.
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
<a name="pnp.plugins.push.timedb.influxpush"></a>

### 5.13\. pnp.plugins.push.timedb.InfluxPush

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
    plugin: pnp.plugins.pull.mqtt.MQTTPull
    args:
      host: mqtt
      topic: home/#
  push:
    plugin: pnp.plugins.push.timedb.InfluxPush
    selector: "{'data': payload}"
    args:
      host: influxdb
      port: 8086
      user: root
      password: secret
      database: home
      protocol: "{payload.levels[2]},room={payload.levels[1]} {payload.levels[3]}={payload.payload}"

```
<a name="pnp.plugins.push.mqtt.mqttpush"></a>

### 5.14\. pnp.plugins.push.mqtt.MQTTPush

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
    [https://mosquitto.org/man/mqtt-7.html](https://mosquitto.org/man/mqtt-7.html).

__Result__

For chaining of pushes the payload is simply returned as is.

__Examples__

```yaml
- name: mqtt
  pull:
    plugin: pnp.plugins.pull.simple.Count
  push:
    # Will push the counter to the 'home/counter/state' topic
    plugin: pnp.plugins.push.mqtt.MQTTPush
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
  push:
    plugin: pnp.plugins.push.mqtt.MQTTPush
    # Lets override the topic via envelope mechanism
    # Will publish even counts on topic 'even' and uneven counts on 'uneven'
    selector: "{'data': data, 'topic': 'even' if int(data) % 2 == 0 else 'uneven'}"
    args:
      host: localhost
      port: 1883
```

<a name="changelog"></a>

## 6\. Changelog

We cannot ensure not to introduce any breaking changes to interfaces / behaviour. This might occur every commit whether it is
intended or by accident. Nevertheless we try to list breaking changes in the changelog that we are aware of.
You are encouraged to specify explicitly the version in your dependency tools, e.g.:

    pip install pnp==0.10.0

* **0.11.0** Introduces the pull.zway.ZwayReceiver and pull.sensor.OpenWeather component.
 Introduces logging configurations. Integrates dictmentor package to augment configuration.
* **0.10.0** Introduces engines. You are not enforced to explicitly use one and backward compatibility with
legacy configs is given (actually the example configs work as they did before the change). So there shouldn't be any breaking change.
* ... -> no history
