# Pull 'n' Push 0.5.0

Pulls data from sources and pushes it to sinks

## Simple example

The best is yet to come...

## Pulls

TODO: What is a pull
TODO: Tell about resolving args with envvars

### ZwayPoll

Below are some common request examples.

**Fibaro Motion Sensor**
* Temperature `http://zwayhost:8083/ZWaveAPI/Run/devices[deviceid].instances[0].commandClasses[49].data[1].val.value`
* Luminescence `http://zwayhost:8083/ZWaveAPI/Run/devices[deviceid].instances[0].commandClasses[49].data[3].val.value`

**fibaro Wallplug**
* Meter `http://zwayhost:8083/ZWaveAPI/Run/devices[deviceid].instances[0].commandClasses[50].data[0].val.value`

**Thermostat (Danfoss / other should work as well)**
* Setpoint `http://zwayhost:8083/ZWaveAPI/Run/devices[deviceid].instances[0].commandClasses[67].data[1].val.value`

**Battery operated devices**
* Battery level `http://zwayhost:8083/ZWaveAPI/Run/devices[deviceid].instances[0].commandClasses[128].data.last.value`

Your request can be tested via the zway-test tool. It will use the same mechanics as the the `ZwayPoll` Pull-Plugin.
Set user and password by environment variables to make it work.

    export ZWAY_USER=<username>
    export ZWAY_PASSWORD=<password>
    zway-test http://zwayhost:8083/ZWaveAPI/Run/devices[deviceid].instances[0].Battery.data.last.value