# Changelog

We cannot ensure not to introduce any breaking changes to interfaces / behaviour. This might occur every commit whether it is
intended or by accident. Nevertheless we try to list breaking changes in the changelog that we are aware of.
You are encouraged to specify explicitly the version in your dependency tools, e.g.:

    pip install pnp==0.10.0

**Next release (~0.18.1)**
* Fixes `ignore_overflow` of `pull.sensor.Sound` plugin (which actually has the opposite effect)

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