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
5\.  [Useful hints](#usefulhints)  
5.1\.  [Configuration checking](#configurationchecking)  
5.2\.  [Logging (0.11.0+)](#logging0.11.0+)  
5.3\.  [dictmentor (0.11.0+)](#dictmentor0.11.0+)  
5.4\.  [Advanced selector expressions (0.12.0+)](#advancedselectorexpressions0.12.0+)  
5.5\.  [UDF Throttle (0.15.0+)](#udfthrottle0.15.0+)  
5.6\.  [Docker images](#dockerimages)  
6\.  [Plugins](#plugins)  
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
      interval: 1s
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
      interval: 1s
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
      interval: 1s
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
      interval: 1s
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

An engine is the actual code that executes the workflow of pnp (`pull` -> `selector` -> `push`).
There are different engines for different use cases.

Click [here](https://github.com/HazardDede/pnp/blob/master/docs/engines/README.md) to get a complete overview of all available engines

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

A simple slack logging confiuration that will log warnings and errors to a slack channel looks like this;

```yaml
version: 1
disable_existing_loggers: False

formatters:
    simple:
        format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

handlers:
    console:
        class: logging.StreamHandler
        formatter: simple
        stream: ext://sys.stdout

    slack:
        level: WARNING  # Do not use DEBUG - This will result in a recursion (cause slacker is using urllib which uses logging)
        api_key: '<your_api_key>'  # Retrieve from api.slack.com
        class: pnp.logging.SlackHandler  # Do not change
        channel: '#alerts'  # The channel to use
        ping_level: ERROR  # Ping users when the message has this severity
        ping_users:  # Ping these users (can be real name, display name, internal name, ...)
          - dede

root:
    level: INFO
    handlers:
        - slack
        - console
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
      interval: 1s
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
        interval: 1s
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

A complete list of plugins is available [here](https://github.com/HazardDede/pnp/blob/master/docs/plugins/README.md)


<a name="changelog"></a>

## 7\. Changelog

We cannot ensure not to introduce any breaking changes to interfaces / behaviour. This might occur every commit whether it is
intended or by accident. Nevertheless we try to list breaking changes in the changelog that we are aware of.
You are encouraged to specify explicitly the version in your dependency tools, e.g.:

    pip install pnp==0.10.0

**0.20.2**
* Bugfix: Fixes udf throttling to take arguments into account for result caching
* Refactors udf throttling / caching code to be more pythonic
* Adjusts `pull.simple` components to act like polling components

**0.20.1**
* Bugfix: Socket shutdown of `pull.net.PortProbe` sometimes fails in rare occasions. Is now handled properly

**0.20.0**
* Adds `push.notify.Slack` to push a message to a specified slack channel
* Adds `pull.trigger.Web` to externally trigger poll actions
* Breaking: Slightly changes the behaviour of `udf.simple.Memory`. See [docs](https://github.com/HazardDede/pnp/blob/master/docs/plugins/udf/simple.Memory/index.md)

**0.19.1**
* Bugfix: Adds bug workaround in `schiene` package used by `pull.traffic.DeutscheBahn`
* Bugfix: Adds exception message truncation for `logging.SlackHandler` to ensure starting and ending backticks (code-view)

**0.19.0**
* Adds `pull.traffic.DeutscheBahn` to poll the `Deutsche Bahn` website using the `schiene` package to find the next scheduled trains
* Adds `push.simple.Wait` to interrupt the execution for some specified amount of time
* Breaking: Component `pull.sensor.Sound` can now check multiple sound files for similarity. The configurational arguments changed. Have a look at the docs
* Breaking: Fixes `ignore_overflow` of `pull.sensor.Sound` plugin (which actually has the opposite effect)
* Breaking: `pull.sensor.Sound` can optionally trigger a cooldown event after the cooldown period expired. This is useful for a binary sensor to turn it off after the cooldown
* Adds slack logging handler to log messages to a slack channel and optionally ping users
* Adds `pull.net.PortProbe` plugin to probe a specific port if it's being used

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
