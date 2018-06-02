# Pull 'n' Push 0.6.0

[![Build Status](https://travis-ci.org/HazardDede/pnp.svg?branch=master)](https://travis-ci.org/HazardDede/pnp)

Pulls data from sources and pushes it to sinks.


## Installation

    git clone https://github.com/HazardDede/pnp.git
    cd pnp
    pip3 install --process-dependency-links .  # Vanilla installation without extras

    
### Optional extras

* dht: Enables `pnp.plugins.pull.sensor.DHT` (temperature and humidity sensor). Only works on ARM-based systems (like raspberry, arduino)
* fswatcher: Enables `pnp.plugins.pull.fs.FileSystemWatcher` (Watch file system for created, modified, 
deleted, moved files)
* faceR: Enables `pnp.plugins.push.ml.FaceR` (Screen image files for known faces)

Installation with extras:
    
    pip3 install --process-dependency-links .[dht,fswatcher,faceR]


## Getting started

Define `pulls` to suck/pull data from source systems.
Define one `push` or multiple `pushes` per pull to transfer the pulled data anywhere else (you only need a plugin that 
knows how to handle the target). You can define your configurations in `yaml` or `json`. 
It is up to you. I prefer yaml...

    - name: hello-world
      pull:
        plugin: pnp.plugins.pull.simple.Repeat
        args:
          wait: 1
          repeat: "Hello World"
      push:
        - plugin: pnp.plugins.push.simple.Echo
        
Copy this configuration and create the file `helloworld.yaml`. Run it:

    pnp helloworld.yaml

This example yields the string 'Hello World' every second.


## Building Blocks

Below the basic building blocks of pull 'n' push are explained in more detail


### Pull

As stated before pulls fetch data from various source systems and/or apis. Please see the section plugins for already
implemented pulls. To instantiate a pull by configuration file you only have to provide it's fully qualified name
and the argument that should be passed.

    - name: example
      pull:
        plugin: pnp.plugins.pull.mqtt.MQTTPull
        args:
          host: localhost
          port: 1883
          topic: test/#
        
The above snippet will create a pull that listens on the topic test/# on a mqtt broker. The output of the pull
is a dictionary that contains the topic, levels and the actual payload.

    # When the message 'Here i am' arrives on the topic 'test/foo/bar' then the output will look like that:
    {'topic': 'test/foo/bar', 'levels': ['test', 'foo', 'bar'], 'payload': 'Here i am'}


### Push

A pull passes its data to multiple pushes to transfer/transform the data. For example a push might save sensor data
to influx or dump a file to the file system.

    - name: example
      pull:
        plugin: pnp.plugins.pull.mqtt.MQTTPull
        args:
          host: localhost
          port: 1883
          topic: test/#
      push:
        - plugin: pnp.plugins.fs.push.FileDump
          args:
            directory: "/tmp"
            binary_mode: False
        - plugin: pnp.plugins.push.simple.Echo
      
The above snippet adds two pushes to the already known pull. The first push takes the incoming data and dumps it into
the specified directory as a textfile. The second push just prints out the incoming data.


### Selector

Sometimes the output of a pull needs to be transformed before the specified push can handle it. `Selectors` to the 
rescue. Given our input we decide to just dump the payload and print out the first level of the topic.

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
      
Easy as that. We can reference our incoming data via `data` or `payload`.


### Dependencies

By default any pushes will execute in parallel (not completly true) when new incoming data is available.
But now it would be nice if we could chain pushes together. So that the output if one push becomes the 
input of the next push. The good thing is: Yes we can.

Back to our example let's assume we want to print out the path to the created file dump after the dump is created.

    - name: example
      pull:
        plugin: pnp.plugins.pull.mqtt.MQTTPull
        args:
          host: localhost
          port: 1883
          topic: test/#
      push:
        - plugin: pnp.plugins.fs.push.FileDump
          selector: data.payload
          args:
            directory: "/tmp"
            binary_mode: False
          deps: 
            - plugin: pnp.plugins.push.simple.Echo
        - plugin: pnp.plugins.push.simple.Echo
          selector: data.levels[0]
        
As you can see we just add a dependant push to the previous one.


## Plugins

### pnp.plugins.pull.ZwayPoll

Please find below a configuration example

    # Please make sure to adjust url and device ids
    # Username and Password are injected from environment variables:
    #     export ZWAY_USER=admin
    #     export ZWAY_PASSWORD=secret_one
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
