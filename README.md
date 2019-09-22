# Pull 'n' Push

[![PyPI version](https://badge.fury.io/py/pnp.svg)](https://badge.fury.io/py/pnp)
[![Build Status](https://travis-ci.org/HazardDede/pnp.svg?branch=master)](https://travis-ci.org/HazardDede/pnp)
[![Coverage Status](https://coveralls.io/repos/github/HazardDede/pnp/badge.svg?branch=master)](https://coveralls.io/github/HazardDede/pnp?branch=master)
[![Docker: hub](https://img.shields.io/badge/docker-hub-brightgreen.svg)](https://cloud.docker.com/u/hazard/repository/docker/hazard/pnp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


> Pulls data from sources and pushes it to sinks.

1\.  [Installation](#installation)  
2\.  [Getting started](#gettingstarted)  
3\.  [Runner](#runner)  
4\.  [Building Blocks](#buildingblocks)  
4.1\.  [Pull](#pull)  
4.2\.  [Push](#push)  
4.3\.  [Selector](#selector)  
4.4\.  [Dependencies](#dependencies)  
4.5\.  [Envelope (0.7.1+)](#envelope0.7.1+)  
4.6\.  [Payload unwrapping](#payloadunwrapping)  
4.7\.  [Engines (0.10.0+)](#engines0.10.0+)  
4.7.1\.  [pnp.engines.SequentialEngine](#pnp.engines.sequentialengine)  
4.7.2\.  [pnp.engines.ThreadEngine](#pnp.engines.threadengine)  
4.7.3\.  [pnp.engines.ProcessEngine](#pnp.engines.processengine)  
4.7.4\.  [pnp.engines.AsyncEngine (0.18.0+)](#pnp.engines.asyncengine0.18.0+)  
5\.  [Useful hints](#usefulhints)  
5.1\.  [Configuration checking](#configurationchecking)  
5.2\.  [Logging (0.11.0+)](#logging0.11.0+)  
5.3\.  [dictmentor (0.11.0+)](#dictmentor0.11.0+)  
5.4\.  [Advanced selector expressions (0.12.0+)](#advancedselectorexpressions0.12.0+)  
5.5\.  [UDF Throttle (0.15.0+)](#udfthrottle0.15.0+)  
5.6\.  [Docker images](#dockerimages)  
6\.  [Plugins](#plugins)  
6.1\.  [pnp.plugins.pull.camera.MotionEyeWatcher](#pnp.plugins.pull.camera.motioneyewatcher)  
6.2\.  [pnp.plugins.pull.fitbit.Current](#pnp.plugins.pull.fitbit.current)  
6.3\.  [pnp.plugins.pull.fitbit.Devices](#pnp.plugins.pull.fitbit.devices)  
6.4\.  [pnp.plugins.pull.fitbit.Goal](#pnp.plugins.pull.fitbit.goal)  
6.5\.  [pnp.plugins.pull.fs.FileSystemWatcher](#pnp.plugins.pull.fs.filesystemwatcher)  
6.6\.  [pnp.plugins.pull.fs.Size](#pnp.plugins.pull.fs.size)  
6.7\.  [pnp.plugins.pull.ftp.Server](#pnp.plugins.pull.ftp.server)  
6.8\.  [pnp.plugins.pull.gpio.Watcher](#pnp.plugins.pull.gpio.watcher)  
6.9\.  [pnp.plugins.pull.hass.State](#pnp.plugins.pull.hass.state)  
6.10\.  [pnp.plugins.pull.http.Server](#pnp.plugins.pull.http.server)  
6.11\.  [pnp.plugins.pull.monitor.Stats](#pnp.plugins.pull.monitor.stats)  
6.12\.  [pnp.plugins.pull.mqtt.Subscribe](#pnp.plugins.pull.mqtt.subscribe)  
6.13\.  [pnp.plugins.pull.sensor.DHT](#pnp.plugins.pull.sensor.dht)  
6.14\.  [pnp.plugins.pull.sensor.MiFlora](#pnp.plugins.pull.sensor.miflora)  
6.15\.  [pnp.plugins.pull.sensor.OpenWeather](#pnp.plugins.pull.sensor.openweather)  
6.16\.  [pnp.plugins.pull.sensor.Sound](#pnp.plugins.pull.sensor.sound)  
6.17\.  [pnp.plugins.pull.simple.Count](#pnp.plugins.pull.simple.count)  
6.18\.  [pnp.plugins.pull.simple.Cron](#pnp.plugins.pull.simple.cron)  
6.19\.  [pnp.plugins.pull.simple.Repeat](#pnp.plugins.pull.simple.repeat)  
6.20\.  [pnp.plugins.pull.zway.ZwayPoll](#pnp.plugins.pull.zway.zwaypoll)  
6.21\.  [pnp.plugins.pull.zway.ZwayReceiver](#pnp.plugins.pull.zway.zwayreceiver)  
6.22\.  [pnp.plugins.push.fs.FileDump](#pnp.plugins.push.fs.filedump)  
6.23\.  [pnp.plugins.push.hass.Service](#pnp.plugins.push.hass.service)  
6.24\.  [pnp.plugins.push.http.Call](#pnp.plugins.push.http.call)  
6.25\.  [pnp.plugins.push.mail.GMail](#pnp.plugins.push.mail.gmail)  
6.26\.  [pnp.plugins.push.ml.FaceR](#pnp.plugins.push.ml.facer)  
6.27\.  [pnp.plugins.push.mqtt.Discovery](#pnp.plugins.push.mqtt.discovery)  
6.28\.  [pnp.plugins.push.mqtt.Publish](#pnp.plugins.push.mqtt.publish)  
6.29\.  [pnp.plugins.push.notify.Pushbullet](#pnp.plugins.push.notify.pushbullet)  
6.30\.  [pnp.plugins.push.simple.Echo](#pnp.plugins.push.simple.echo)  
6.31\.  [pnp.plugins.push.simple.Execute](#pnp.plugins.push.simple.execute)  
6.32\.  [pnp.plugins.push.storage.Dropbox](#pnp.plugins.push.storage.dropbox)  
6.33\.  [pnp.plugins.push.timedb.InfluxPush](#pnp.plugins.push.timedb.influxpush)  
6.34\.  [pnp.plugins.udf.hass.State](#pnp.plugins.udf.hass.state)  
6.35\.  [pnp.plugins.udf.simple.Counter](#pnp.plugins.udf.simple.counter)  
6.36\.  [pnp.plugins.udf.simple.FormatSize](#pnp.plugins.udf.simple.formatsize)  
6.37\.  [pnp.plugins.udf.simple.Memory](#pnp.plugins.udf.simple.memory)  
7\.  [Changelog](#changelog)  

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

<a name="runner"></a>

## 3\. Runner

```
> pnp --help
Pull 'n' Push

Usage:
  pnp [(-c | --check)] [(-v | --verbose)] [--log=<log_conf>] <configuration>
  pnp (-h | --help)
  pnp --version

Options:
  -c --check        Only check configuration and do not run it.
  -v --verbose      Switches log level to debug.
  --log=<log_conf>  Specify logging configuration to load.
  -h --help         Show this screen.
  --version         Show version.
```

<a name="buildingblocks"></a>

## 4\. Building Blocks

Below the basic building blocks of pull 'n' push are explained in more detail


<a name="pull"></a>

### 4.1\. Pull

As stated before pulls fetch data from various source systems and/or apis. Please see the section plugins for already
implemented pulls. To instantiate a pull by configuration file you only have to provide it's fully qualified name
and the argument that should be passed.

```yaml
- name: example
  pull:
    plugin: pnp.plugins.pull.mqtt.Subscribe
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

### 4.2\. Push

A pull passes its data to multiple pushes to transfer/transform the data. For example a push might save sensor data
to influx or dump a file to the file system.

```yaml
- name: example
  pull:
    plugin: pnp.plugins.pull.mqtt.Subscribe
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    - plugin: pnp.plugins.push.fs.FileDump
      args:
        directory: "/tmp"
        binary_mode: false
    - plugin: pnp.plugins.push.simple.Echo

```
      
The above snippet adds two pushes to the already known pull. The first push takes the incoming data and dumps it into
the specified directory as a textfile. The second push just prints out the incoming data.


<a name="selector"></a>

### 4.3\. Selector

Sometimes the output of a pull needs to be transformed before the specified push can handle it. `Selectors` to the 
rescue. Given our input we decide to just dump the payload and print out the first level of the topic.

```yaml
- name: example
  pull:
    plugin: pnp.plugins.pull.mqtt.Subscribe
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    - plugin: pnp.plugins.push.fs.FileDump
      selector: data.payload
      args:
        directory: "/tmp"
        binary_mode: false
    - plugin: pnp.plugins.push.simple.Echo
      selector: data.levels[0]

```

Easy as that. We can reference our incoming data via `data` or `payload`.


<a name="dependencies"></a>

### 4.4\. Dependencies

By default any pushes will execute in parallel (not completly true) when new incoming data is available.
But now it would be nice if we could chain pushes together. So that the output if one push becomes the 
input of the next push. The good thing is: Yes we can.

Back to our example let's assume we want to print out the path to the created file dump after the dump is created.

```yaml
- name: example
  pull:
    plugin: pnp.plugins.pull.mqtt.Subscribe
    args:
      host: localhost
      port: 1883
      topic: test/#
  push:
    - plugin: pnp.plugins.push.fs.FileDump
      selector: data.payload
      args:
        directory: "/tmp"
        binary_mode: false
      deps:
        - plugin: pnp.plugins.push.simple.Echo
    - plugin: pnp.plugins.push.simple.Echo
      selector: data.levels[0]

```
        
As you can see we just add a dependant push to the previous one.


<a name="envelope0.7.1+"></a>

### 4.5\. Envelope (0.7.1+)

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
    selector:
      file_name: "lambda data: str(data)"
      extension: ".cnt"
      data: "lambda data: data"
    args:
      directory: "/tmp/counter"
      file_name: "counter"  # Overridden by envelope
      extension: ".txt"  #  Overridden by envelope
      binary_mode: false  # text mode

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
        selector:
          data: "lambda data: data"

<a name="payloadunwrapping"></a>

### 4.6\. Payload unwrapping

By default any payload that is provided to a push will be "as-is". If the payload is an iterable, it is possible
to `unwrap` each individual item of the iterable and providing that item to the push instead of the whole list. Yes, now
you can perform for each loops for pushes.

```yaml
- name: unwrapping
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      wait: 1
      repeat:
        - 1
        - 2
        - 3
  push:
    - plugin: pnp.plugins.push.simple.Echo
      unwrap: true

```

Hint: Selector expressions are applied after unwrapping. So the selector is applied to each individual item.
If you need the selector to augment your list, use a `push.simple.Nop` with `unwrap = False` and a dependent push.


```yaml
- name: unwrapping
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      wait: 1
      repeat:
        - 1
        - 2
        - 3
  push:
    - plugin: pnp.plugins.push.simple.Nop
      selector: "data + [4, 5, 6]"
      unwrap: false  # Which is the default
      deps:
        - plugin: pnp.plugins.push.simple.Echo
          unwrap: true

```


<a name="engines0.10.0+"></a>

### 4.7\. Engines (0.10.0+)

If you do not specify any engine the `ThreadEngine` is chosen by default accompanied by the `AdvancedRetryHandler`.
This keeps maximum backwards compatibility.

Remark: This will probably change in the near future in favor to the `AsyncEngine`.

<a name="pnp.engines.sequentialengine"></a>

#### 4.7.1\. pnp.engines.SequentialEngine

By using the `Sequential` engine you can run your configs as scripts. Given the example below, the "script" will
end when it has finished counting to 3. Make sure to use the `NoRetryHandler` to actually end the runner when
the pull has finished instead of retrying the "failed" `pull`. You cn only run a single task not multiple.
When you want to run multiple task in a concurrent manner you have to use the `ThreadEngine`, `ProcessEngine` or `AsyncEngine`.

```yaml
#### Simple sequential handler
#### Counts from 1 to 3 and then terminates
engine: !engine
  type: pnp.engines.SequentialEngine
  retry_handler: !retry
    # Is the key to termination after counting has finished
    type: pnp.engines.NoRetryHandler
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

<a name="pnp.engines.threadengine"></a>

#### 4.7.2\. pnp.engines.ThreadEngine

```yaml
#### Will use threads to accomplish concurrency
#### Drawback: If a plugin does not stop gracefully the termination will hang...
engine: !engine
  type: pnp.engines.ThreadEngine
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

<a name="pnp.engines.processengine"></a>

#### 4.7.3\. pnp.engines.ProcessEngine

```yaml
#### Will use multiprocessing to accomplish concurrency
#### Drawback: Some plugins might not work or need to be aware of
engine: !engine
  type: pnp.engines.ProcessEngine
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

<a name="pnp.engines.asyncengine0.18.0+"></a>

#### 4.7.4\. pnp.engines.AsyncEngine (0.18.0+)

```yaml
#### Will use asyncio to accomplish concurrency

engine: !engine
  type: pnp.engines.AsyncEngine
  retry_handler: !retry
    type: pnp.engines.SimpleRetryHandler
tasks:
  - name: async
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        wait: 1
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo

```

<a name="usefulhints"></a>

## 5\. Useful hints

<a name="configurationchecking"></a>

### 5.1\. Configuration checking

You can check your pnp configuration file by starting pnp with the `-c | --check` flag set. This will only run
the initializer but not execute the configuration.

```bash
pnp --check <pnp_configuration>
```

<a name="logging0.11.0+"></a>

### 5.2\. Logging (0.11.0+)

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


<a name="dictmentor0.11.0+"></a>

### 5.3\. dictmentor (0.11.0+)

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
---
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

<a name="advancedselectorexpressions0.12.0+"></a>

### 5.4\. Advanced selector expressions (0.12.0+)

Instead of string-only selector expressions, you may now use complex dictionary and/or list constructs in your yaml
to define a selector expression. If you use a dictionary or a list make sure to provide "real" selectors as a
lambda expression, so the evaluator can decide if this is a string literal or an expression to evaluate.

The configuration below will repeat `{'hello': 'Hello', 'words': ['World', 'Moon', 'Mars']}`.

```yaml
- name: selector
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      wait: 1
      repeat: "Hello World Moon Mars"
  push:
    - plugin: pnp.plugins.push.simple.Echo
      selector:
        hello: "lambda payload: payload.split(' ')[0]"
        words:
          - "lambda payload: payload.split(' ')[1]"
          - "lambda payload: payload.split(' ')[2]"
          - "lambda payload: payload.split(' ')[3]"
```

Before the advanced selector feature your epxressions would have probably looked similiar to this:
`dict(hello=payload.split(' ')[0], words=[payload.split(' ')[1], payload.split(' ')[2], payload.split(' ')[3]])`.
The first one is more readable, isn't it?

Additional example:

```yaml
---
- name: selector
  pull:
    plugin: pnp.plugins.pull.simple.Repeat
    args:
      wait: 1
      repeat: "Hello World"
  push:
    - plugin: pnp.plugins.push.simple.Echo
      # Returns: 'World'
      selector: "str(payload.split(' ')[0])"  # no complex structure. Evaluator assumes that this is an expression -> you do not need a lambda
    - plugin: pnp.plugins.push.simple.Echo
      selector:  # Returns {'header': 'this is a header', 'data': 'World', 'Hello': 'World'}
        header: this is a header  # Just string literals
        data: "lambda data: data.split(' ')[1]"  # Value is lambda and therefore evaluated
        "lambda data: str(data.split(' ')[0])": "lambda data: data.split(' ')[1]"  # Both are lambdas and therefore evaluated
    - plugin: pnp.plugins.push.simple.Echo
      selector:  # Returns ['foo', 'bar', 'Hello', 'World']
        - foo  # String literal
        - bar  # String literal
        - "lambda d: d.split(' ')[0]"  # Lambda -> evaluate the expression
        - "lambda d: d.split(' ')[1]"  # Lambda -> evaluate the expression

```

<a name="udfthrottle0.15.0+"></a>

### 5.5\. UDF Throttle (0.15.0+)

Consider the following situation: You have a selector that uses a udf to fetch a state from an external system.
The state won't change so often, but your selector will fetch the state every time a pull transports a payload to
the push. You want to decrease the load on the external system and you want to increase throughput. `Throttle` to the
rescue. Specifying `throttle` when instantiating your `udf` will manage that your `udf` will only call the external
system once and cache the result. Subsequent calls will either return the cached result or call the external system again
when a specified time has passed since the last call that actually fetched a result from the external system.

Example:

```yaml
udfs:
  - name: count  # Instantiate a Counter user defined function
    plugin: pnp.plugins.udf.simple.Counter
    args:  # The presence of args tells pnp to instantiate a Counter - important because it has a state (the actual count)
      init: 1
      # Will only call the counter if 10 seconds passed between current call and last call.
      # In the meantime a cached result will be returned.
      throttle: 5s
tasks:
  - name: hello-world
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        wait: 1
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo
        selector:
          counter: "lambda d: count()"

```


<a name="dockerimages"></a>

### 5.6\. Docker images

```bash
# Mount the task and logging configuration when starting up the container
docker run --rm \
    -v /path/to/pnp/config/01_hello_world.yaml:/config/config.yaml \
    -v /path/to/logging/config/file.logging:/config/logging.yaml \
    hazard/pnp:latest
```


<a name="plugins"></a>

## 6\. Plugins

<a name="pnp.plugins.pull.camera.motioneyewatcher"></a>

### 6.1\. pnp.plugins.pull.camera.MotionEyeWatcher

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
### Basic example - just echoing events
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
### Publishes a binary motion sensor to home assistant via mqtt discovery  ...
### ... and uploads movies to dropbox when nobody is home and motion is detected
### ... and publishes images to home assistant by a push camera

### Make sure to set the following env vars correctly:
### - MOTIONEYE_MEDIA_PATH: The path where motioneye puts the media files
### - MQTT_HOST: Your mqtt host
### - HA_HOST: Your home assistant url (incl. port)
### - HA_TOKEN: Your home assistant long lived access token
### - DROPBOX_API_KEY: Your dropbox api key
### - PUSHBULLET_API_KEY: Your pushbullet api key

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
###!/bin/bash

### Contents of push_camera.sh

IMAGE_FILE=$1

curl -X POST -F "image=@${IMAGE_FILE}" ${HA_HOST}/api/webhook/motion01
```
<a name="pnp.plugins.pull.fitbit.current"></a>

### 6.2\. pnp.plugins.pull.fitbit.Current


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
### Please point your environment variable `FITBIT_AUTH` to your authentication
### configuration
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
<a name="pnp.plugins.pull.fitbit.devices"></a>

### 6.3\. pnp.plugins.pull.fitbit.Devices


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
### Please point your environment variable `FITBIT_AUTH` to your authentication
### configuration
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
<a name="pnp.plugins.pull.fitbit.goal"></a>

### 6.4\. pnp.plugins.pull.fitbit.Goal

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
### Please point your environment variable `FITBIT_AUTH` to your authentication
### configuration
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
<a name="pnp.plugins.pull.fs.filesystemwatcher"></a>

### 6.5\. pnp.plugins.pull.fs.FileSystemWatcher

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
<a name="pnp.plugins.pull.fs.size"></a>

### 6.6\. pnp.plugins.pull.fs.Size

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
<a name="pnp.plugins.pull.ftp.server"></a>

### 6.7\. pnp.plugins.pull.ftp.Server

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
<a name="pnp.plugins.pull.gpio.watcher"></a>

### 6.8\. pnp.plugins.pull.gpio.Watcher

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
<a name="pnp.plugins.pull.hass.state"></a>

### 6.9\. pnp.plugins.pull.hass.State

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
<a name="pnp.plugins.pull.http.server"></a>

### 6.10\. pnp.plugins.pull.http.Server

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
<a name="pnp.plugins.pull.monitor.stats"></a>

### 6.11\. pnp.plugins.pull.monitor.Stats

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
<a name="pnp.plugins.pull.mqtt.subscribe"></a>

### 6.12\. pnp.plugins.pull.mqtt.Subscribe

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

<a name="pnp.plugins.pull.sensor.dht"></a>

### 6.13\. pnp.plugins.pull.sensor.DHT

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
<a name="pnp.plugins.pull.sensor.miflora"></a>

### 6.14\. pnp.plugins.pull.sensor.MiFlora

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
<a name="pnp.plugins.pull.sensor.openweather"></a>

### 6.15\. pnp.plugins.pull.sensor.OpenWeather

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
### Make sure you export your api key with:
###   `export OPENWEATHER_API_KEY=<your_api_key>`
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
<a name="pnp.plugins.pull.sensor.sound"></a>

### 6.16\. pnp.plugins.pull.sensor.Sound

Listens to the microphone in realtime and searches the stream for a specific sound pattern.
Practical example: I use this plugin to recognize my doorbell without tampering with the electrical device ;-)

Requires extra `sound`.

__Arguments__

- **wav_file (str/filepath)**: The file that contains the original sound pattern to listen for.
- **device_index (int, optional)**: The index of the microphone device. Run `pnp_record_sound --list` to get the index.
If not specified pyAudio will try to find a capable device.</br>
- **mode (Union[pearson,std], optional)**: Correlation/similarity method. Default is pearson.</br>
- **sensitivity_offset (float, optional)**: Adjusts sensitivity for similarity.
Positive means less sensitive; negative is more sensitive. You should try out 0.1 steps. Default is 0.0.
- **cool_down (duration literal, optional)**: Prevents the pull to emit more than one sound detection event per
cool down duration. Default is 10 seconds.
- **ignore_overflow (bool, optional)**: If set to True any buffer overflows due to slow realtime processing will be ignored.
    Otherwise an exception will be thrown.

Hints:
* You can list your available input devices: `pnp_record_sound --list`
* You can record a wav file from an input device: `pnp_record_sound <out.wav> <seconds_to_record> --index=<idx>`
* This one is _not_ pre-installed when using the docker image. Would be grateful if anyone can integrate it


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
      device_index:  # The index of the microphone devices. If not specified pyAudio will try to find a capable device
      mode: pearson  # Use pearson correlation coefficient [pearson, std]
      sensitivity_offset: 0.1  # Adjust sensitivity. Positive means less sensitive; negative is more sensitive
      cool_down: 3s  # Prevents the pull to emit more than one sound detection event every 3 seconds
      ignore_overflow: true  # Some devices might be too slow to process the stream in realtime. Ignore any buffer overflow errors.
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
<a name="pnp.plugins.pull.simple.count"></a>

### 6.17\. pnp.plugins.pull.simple.Count

Emits every `wait` seconds a counting value which runs from `from_cnt` to `to_cnt`.
If `to_cnt` is None the counter will count to infinity.

__Arguments__

- **wait (int)**: Wait the amount of seconds before emitting the next counter.
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
      wait: 1
      from_cnt: 1
      to_cnt: 10
  push:
    plugin: pnp.plugins.push.simple.Echo

```
<a name="pnp.plugins.pull.simple.cron"></a>

### 6.18\. pnp.plugins.pull.simple.Cron

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
<a name="pnp.plugins.pull.simple.repeat"></a>

### 6.19\. pnp.plugins.pull.simple.Repeat

Emits every `wait` seconds the same `repeat`.

__Arguments__

- **wait (int)**: Wait the amount of seconds before emitting the next repeat.
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
      wait: 1  # Every second
  push:
    plugin: pnp.plugins.push.simple.Echo

```
<a name="pnp.plugins.pull.zway.zwaypoll"></a>

### 6.20\. pnp.plugins.pull.zway.ZwayPoll

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

<a name="pnp.plugins.pull.zway.zwayreceiver"></a>

### 6.21\. pnp.plugins.pull.zway.ZwayReceiver

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

<a name="pnp.plugins.push.fs.filedump"></a>

### 6.22\. pnp.plugins.push.fs.FileDump

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
<a name="pnp.plugins.push.hass.service"></a>

### 6.23\. pnp.plugins.push.hass.Service

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
### Calls the frontend.set_theme service to oscillate between a "light" and a "dark" theme
- name: hass_service
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 10
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
### Calls the notify.pushbullet service to send a message with the actual counter
- name: hass_service
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 10
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
<a name="pnp.plugins.push.http.call"></a>

### 6.24\. pnp.plugins.push.http.Call

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
### Simple example calling the built-in rest server
### Oscillates between http method GET and POST. Depending on the fact if the counter is even or not.
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
<a name="pnp.plugins.push.mail.gmail"></a>

### 6.25\. pnp.plugins.push.mail.GMail

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
### Pull triggers when a file is created in the specified directory
### The GMail push will send an e-mail to a specific recipient with the created file attached
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
<a name="pnp.plugins.push.ml.facer"></a>

### 6.26\. pnp.plugins.push.ml.FaceR

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
<a name="pnp.plugins.push.mqtt.discovery"></a>

### 6.27\. pnp.plugins.push.mqtt.Discovery

TBD

[https://www.home-assistant.io/docs/mqtt/discovery/](https://www.home-assistant.io/docs/mqtt/discovery/)

__Arguments__

TBD

__Result__

For chaining of pushes the payload is simply returned as is.

__Examples__

```yaml
### Please point your environment variable `FITBIT_AUTH` to your authentication configuration
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
<a name="pnp.plugins.push.mqtt.publish"></a>

### 6.28\. pnp.plugins.push.mqtt.Publish

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
<a name="pnp.plugins.push.notify.pushbullet"></a>

### 6.29\. pnp.plugins.push.notify.Pushbullet

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
### Make sure that you provided PUSHBULETT_API_KEY as an environment variable
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
<a name="pnp.plugins.push.simple.echo"></a>

### 6.30\. pnp.plugins.push.simple.Echo

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
<a name="pnp.plugins.push.simple.execute"></a>

### 6.31\. pnp.plugins.push.simple.Execute

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
      wait: 1
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
      wait: 1
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
<a name="pnp.plugins.push.storage.dropbox"></a>

### 6.32\. pnp.plugins.push.storage.Dropbox

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
### Make sure that you provided DROPBOX_API_KEY as an environment variable
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
<a name="pnp.plugins.push.timedb.influxpush"></a>

### 6.33\. pnp.plugins.push.timedb.InfluxPush

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

<a name="pnp.plugins.udf.hass.state"></a>

### 6.34\. pnp.plugins.udf.hass.State

Fetches the state of an entity from home assistant by a rest-api request.

__Arguments__

- **url (str)**: The url to your home assistant instance (e.g. http://hass:8123)
- **token (str)**: The love live access token to get access to home assistant
- **timeout (Optional[int])**: Tell the request to stop waiting for a reponse after given number of seconds. Default is 5 seconds.

__Call Arguments__

- **entity_id (str)**: The entity to fetch the state<br>
- **attribute (Optional[str])**: Optionally you can fetch the state of one of the entities attributes.
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
<a name="pnp.plugins.udf.simple.counter"></a>

### 6.35\. pnp.plugins.udf.simple.Counter

Memories a counter value which is increased everytime you call the udf.

__Arguments__

- **init (Optional[int])**: The initialization value of the counter. Default is 0.

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
<a name="pnp.plugins.udf.simple.formatsize"></a>

### 6.36\. pnp.plugins.udf.simple.FormatSize

Returns the size of a file (or whatever) as a human readable size (e.g. bytes, KB, MB, GB, TB, PB).
The input is expected to be at byte scale.

__Arguments__

- **size_in_bytes (float|int)**: The size in bytes to format to a human readable format.

__Result__

Returns the argument in a human readable size format.

__Examples__

```yaml
udfs:
  # Defines the udf. name is the actual alias you can call in selector expressions.
  - name: fsize
    plugin: pnp.plugins.udf.simple.FormatSize
    args:
      init: 1
tasks:
  - name: format_size
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
      plugin: pnp.plugins.push.simple.Nop
      selector: "[(k ,v) for k, v in data.items()]"  # Transform the dictionary into a list
      deps:
        plugin: pnp.plugins.push.simple.Echo
        unwrap: true  # Call the push for each individual item in the list
        selector:
          object: "lambda d: d[0]"
          data: "lambda d: fsize(d[1])"

```
<a name="pnp.plugins.udf.simple.memory"></a>

### 6.37\. pnp.plugins.udf.simple.Memory

Returns a previously memorized value when called.

__Arguments__

- **init (any, optional)**: The initial memory of the plugin. Default is None.

__Call Arguments__

- **new_memory (any, optional)**: After emitting the current memorized value the current memory is overwritten by this value.
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

<a name="changelog"></a>

## 7\. Changelog

We cannot ensure not to introduce any breaking changes to interfaces / behaviour. This might occur every commit whether it is
intended or by accident. Nevertheless we try to list breaking changes in the changelog that we are aware of.
You are encouraged to specify explicitly the version in your dependency tools, e.g.:

    pip install pnp==0.10.0

**0.18.0**
* Integrates an asyncio featured/powered engine. I think this will be the default in the future. Stay tuned!

**0.17.1**
* Fixes missing typing-extensions dependency
* Fixes urllib3 versions due to requests incompatibilities

**0.17.0**
* Adjusts inline documentation - refers to github documentation
* Refactors a majority of codebase to comply to pylint linter
* Integrates yamllint as linter
* Refactores RetryDirective (namedtuple to attr class)
* Adds decorators for parsing the envelope in a push context
* Breaking: Removes `push.simple.Execute` and replace it by `push.simple.TemplatedExecute`
* Adjusts method `logger` in plugin classes to automatically prepend plugin name
* Integrates coveralls
* Adds `pull.ftp.Server` plugin
* Adds lazy configuration property to `push.ml.FaceR` (basically to test initialization of FaceR without installing face-recognition and dlib)
* Adds `pull.fs.Size` plugin
* Adds typing for most of the core codebase and adds mypy as linter

**0.16.0**
* Adds `ignore_overflow` argument to `pull.sensor.Sound` to ignore buffer overflows errors on slow devices
* Possible breaking: Adds raspberrypi specific stats (under voltage, throttle, ...) to `pull.monitor.stats`
* Professionalizes docker image build process / Testing the container
* Documentation cosmetics
* Adds cron-like pull `pull.simple.Cron`
* Adds `pull.camera.MotionEyeWatcher` to watch a MotionEye directory to emit events
* Adds `push.hass.Service` to call home assistant services by rest-api
* Breaking: New default value of `cwd` argument of `push.simple.Execute` is now the folder where the invoked pnp-configuration is located and not the current working directory anymore
* Adds `push.simple.TemplatedExecute` as a replacement for `push.simple.Execute`
* Adds cron-expressions to polling base class
* Adds `pull.sensor.MiFlora` plugin to periodically poll xiaomi miflora devices

**0.15.0**
* Adds `push.mail.GMail` to send e-mails via the gmail api
* Adds `throttle`-feature to user defined functions via base class
* Adds `pull.sensor.Sound` to listen to the microphone's sound stream for occurrence of a specified sound

**0.14.0**
* Adds UDF (user defined functions)
* Adds UDF `udf.hass.State` to request the current state of an entity (or one of it's attributes) from home assistant
* Makes selector expressions in complex structures (dicts / lists) more explicit using lambda expressions with mandatory payload argument.
  This will probably break configs that use complex expressions containing lists and/or dictionaries
* Adds `pull.hass.State` to listen to state changes in home assistant
* Fixes bug in `pull.fitbit.Goal` when fetching weekly goals (so far daily goals were fetched too)
* Adds UDF `udf.simple.Memory` to memorize values to access them later

**0.13.0**
* Adds `pull.fitbit.Current`, `pull.fitbit.Devices`, `pull.fitbit.Goal` plugins to request data from fitbit api
* Adds `push.mqtt.Discovery` to create mqtt discovery enabled devices for home assistant. [Reference](https://www.home-assistant.io/docs/mqtt/discovery/)
* Adds `unwrapping`-feature to pushes

**0.12.0**
* Adds additional argument `multi` (default False) to `push.mqtt.MQTTPush` to send multiple messages to the broker if
the payload is a dictionary (see plugin docs for reference)
* Adds plugin `pull.monitor.Stats` to periodically emit stats about the host system
* Adds plugin `push.notify.Pushbullet` to send message via the `pushbullet` service
* Adds plugin `push.storage.Dropbox` to upload files to a `dropbox` account/app
* Adds feature to use complex lists and/or dictionary constructs in selector expressions
* Adds plugin `pull.gpio.Watcher` (extra `gpio`) to watch gpio pins for state changes. Only works on raspberry
* Adds plugin `push.simple.Execute` to run commands in a shell
* Adds extra `http-server` to optionally install `flask` and `gevent` when needed
* Adds utility method to check for installed extras
* Adds `-v | --verbose` flag to pnp runner to switch logging level to `DEBUG`. No matter what...

**0.11.3** 
* Adds auto-mapping magic to the `pull.zway.ZwayReceiver`.
* Adds humidity and temperature offset to dht

**0.11.2** 
* Fixes error catching of `run_pending` in `Polling` base class

**0.11.1** 
* Fixes resolution of logging configuration on startup

**0.11.0** 
* Introduces the pull.zway.ZwayReceiver and pull.sensor.OpenWeather component
* Introduces logging configurations. Integrates dictmentor package to augment configuration

**0.10.0** 
* Introduces engines. You are not enforced to explicitly use one and backward compatibility with
legacy configs is given (actually the example configs work as they did before the change). 
So there shouldn't be any breaking change.
