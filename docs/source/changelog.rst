Changelog
=========

**0.28.0**

* **Feature**: Implements yaml tags !env and !include `#43 <https://github.com/HazardDede/pnp/pull/43>`_
* **Fix**: Fixes import issue on recent scipy version `#42 <https://github.com/HazardDede/pnp/pull/42>`_
* **Fix**: Bumps dependency ``speedtest-cli`` to fix a bug that appears on empty server ids `#44 <speedtest-cli>`_

**0.27.0**

* **Breaking**: Migrates from sanic to fastapi (some endpoints have slightly changed; see openapi docs) `#34 <https://github.com/HazardDede/pnp/pull/34>`_
* **Breaking**: Deprecates / Removes ``push.notify.Pushbullet`` `#35 <https://github.com/HazardDede/pnp/pull/35>`_
* **Breaking**: Deprecates / Removes ``pull.zway.ZwayReceiver`` `#36 <https://github.com/HazardDede/pnp/pull/36>`_
* **Breaking**: Deprecates / Removes ``push.mail.GMail`` `#37 <https://github.com/HazardDede/pnp/pull/37>`_
* **Breaking**: Deprecates / Removes ``pull.traffic.DeutscheBahn`` `#38 <https://github.com/HazardDede/pnp/pull/38>`_
* **Breaking**: Deprecates / Removes ``pull.camera.MotionEyeWatcher`` `#39 <https://github.com/HazardDede/pnp/pull/39>`_
* **Breaking**: Deprecates / Removes ``pull.sensor.OpenWeather`` `#40 <https://github.com/HazardDede/pnp/pull/40>`_
* **Breaking (dev)**: Refactors the plugin interface to better distinguish between sync / async plugins to provide a simpler developer interface `#41 <https://github.com/HazardDede/pnp/pull/41>`_
* **Breaking**: Removes `enable_swagger` from the api configuration properties `#41 <https://github.com/HazardDede/pnp/pull/41>`_
* **Breaking (dev)**: Replaces `auto_str` decorator by `ReprMixin` based on `basic_repr` from `fastcore` package `#41 <https://github.com/HazardDede/pnp/pull/41>`_
* **Feature**: Migrates from `attrs` to pydantic for container objects `#41 <https://github.com/HazardDede/pnp/pull/41>`_
* **Feature**: Introduces a runner to start up an application context `#41 <https://github.com/HazardDede/pnp/pull/41>`_
* **Feature**: ``push.mqtt.Discovery``: Adds auto configuration of state- and json attributes topics `#33 <http://github.com/HazardDede/pnp/pull/33/files>`_
* **Feature**: ``push.fs.Zipper``: Adds ``archive_name`` argument to (dynamically) control the name of the created archive `#31 <http://github.com/HazardDede/pnp/pull/31/files>`_

**0.26.1**

* **Fix**: ``pull.net.PortProbe``: Catches a socket error when there is no route to the target host `#32 <https://github.com/HazardDede/pnp/pull/32>`_

**0.26.0**

* **Breaking**: Overhaul of the console scripts (see :ref:`Console Runner`) `#29 <https://github.com/HazardDede/pnp/pull/29>`_
* **Feature**: Colorful printing of configuration and logging `#29 <https://github.com/HazardDede/pnp/pull/29>`_
* **Feature**: Migrates Dockerfile from stretch to buster `#27 <https://github.com/HazardDede/pnp/pull/27>`_
* **Fix**: Proper handling of ``docker stop`` `#30 <https://github.com/HazardDede/pnp/pull/30>`_


**0.25.0**

* **Breaking**: Removes python 3.5 support
* **Breaking**: Updates dependencies
* **Feature**: Adds official python 3.8 support
* **Feature**: Implements **pull.net.Speeedtest** for testing your internet connection speed
* **Fix**: Fixes documentation regarding **push.fs.Zipper**

**0.24.0**

* Migrates the documentation to Read the Docs: `https://pnp.readthedocs.io/en/latest/ <https://pnp.readthedocs.io/en/latest/>`_
* Implements an API
* **Breaking**: **pull.zway.ZwayReceiver** integrates it's endpoint into the api
* **Breaking**: **pull.http.Server** integrates the endpoint into the api
* **Breaking**: Removes engine override from console runner (because we only have a single engine)
* **Breaking**: Removes argresolver support
* **Breaking**: Removes **pull.trigger.TriggerBase** and **pull.trigger.Web**. Tasks can be triggered via the api now

**0.23.0**

* **Breaking**: Removes engines except for AsyncEngine
* Implements **pull.simple.RunOnce** to run a polling component or a push chain once (nice for scripts)
* Migration from **setup.py** to **poetry**
* Migration from **Makefile** to **python-invoke**
* Introduces new configuration concept (interface: **ConfigLoader**)

**0.22.0**

* Updates docker base image to **python 3.7**
* Adds **pull.presence.FritzBoxTracker** to track known devices on a Fritz!Box
* Adds **json_attributes_topic** support to **push.mqtt.Discovery**
* Adds **pull.net.SSLVerify** to check ssl certificates

**0.21.1**

* Feature: Enables arm emulator for arm dockerfile to use docker hub autmated build
* Bugfix: Removes timeout from component **push.storage.Dropbox**

**0.21.0**

* Adds **push.fs.Zipper** to zip dirs and files in the process chain

**0.20.2**

* Bugfix: Fixes udf throttling to take arguments into account for result caching
* Refactors udf throttling / caching code to be more pythonic
* Adjusts **pull.simple** components to act like polling components

**0.20.1**

* Bugfix: Socket shutdown of **pull.net.PortProbe** sometimes fails in rare occasions. Is now handled properly

**0.20.0**

* Adds **push.notify.Slack** to push a message to a specified slack channel
* Adds **pull.trigger.Web** to externally trigger poll actions
* **Breaking**: Slightly changes the behaviour of **udf.simple.Memory**. See [docs](https://github.com/HazardDede/pnp/blob/master/docs/plugins/udf/simple.Memory/index.md)

**0.19.1**

* Bugfix: Adds bug workaround in **schiene** package used by **pull.traffic.DeutscheBahn**
* Bugfix: Adds exception message truncation for **logging.SlackHandler** to ensure starting and ending backticks (code-view)

**0.19.0**

* Adds **pull.traffic.DeutscheBahn** to poll the **Deutsche Bahn** website using the **schiene** package to find the next scheduled trains
* Adds **push.simple.Wait** to interrupt the execution for some specified amount of time
* **Breaking**: Component **pull.sensor.Sound** can now check multiple sound files for similarity. The configurational arguments changed. Have a look at the docs
* **Breaking**: Fixes **ignore_overflow** of **pull.sensor.Sound** plugin (which actually has the opposite effect)
* **Breaking**: **pull.sensor.Sound** can optionally trigger a cooldown event after the cooldown period expired. This is useful for a binary sensor to turn it off after the cooldown
* Adds slack logging handler to log messages to a slack channel and optionally ping users
* Adds **pull.net.PortProbe** plugin to probe a specific port if it's being used

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
* **Breaking**: Removes **push.simple.Execute** and replace it by **push.simple.TemplatedExecute**
* Adjusts method **logger** in plugin classes to automatically prepend plugin name
* Integrates coveralls
* Adds **pull.ftp.Server** plugin
* Adds lazy configuration property to **push.ml.FaceR** (basically to test initialization of FaceR without installing face-recognition and dlib)
* Adds **pull.fs.Size** plugin
* Adds typing for most of the core codebase and adds mypy as linter

**0.16.0**

* Adds **ignore_overflow** argument to **pull.sensor.Sound** to ignore buffer overflows errors on slow devices
* Possible **Breaking**: Adds raspberrypi specific stats (under voltage, throttle, ...) to **pull.monitor.stats**
* Professionalizes docker image build process / Testing the container
* Documentation cosmetics
* Adds cron-like pull **pull.simple.Cron**
* Adds **pull.camera.MotionEyeWatcher** to watch a MotionEye directory to emit events
* Adds **push.hass.Service** to call home assistant services by rest-api
* **Breaking**: New default value of **cwd** argument of **push.simple.Execute** is now the folder where the invoked pnp-configuration is located and not the current working directory anymore
* Adds **push.simple.TemplatedExecute** as a replacement for **push.simple.Execute**
* Adds cron-expressions to polling base class
* Adds **pull.sensor.MiFlora** plugin to periodically poll xiaomi miflora devices

**0.15.0**

* Adds **push.mail.GMail** to send e-mails via the gmail api
* Adds **throttle**-feature to user defined functions via base class
* Adds **pull.sensor.Sound** to listen to the microphone's sound stream for occurrence of a specified sound

**0.14.0**

* Adds UDF (user defined functions)
* Adds UDF **udf.hass.State** to request the current state of an entity (or one of it's attributes) from home assistant
* Makes selector expressions in complex structures (dicts / lists) more explicit using lambda expressions with mandatory payload argument.
  This will probably break configs that use complex expressions containing lists and/or dictionaries
* Adds **pull.hass.State** to listen to state changes in home assistant
* Fixes bug in **pull.fitbit.Goal** when fetching weekly goals (so far daily goals were fetched too)
* Adds UDF **udf.simple.Memory** to memorize values to access them later

**0.13.0**

* Adds **pull.fitbit.Current**, **pull.fitbit.Devices**, **pull.fitbit.Goal** plugins to request data from fitbit api
* Adds **push.mqtt.Discovery** to create mqtt discovery enabled devices for home assistant. [Reference](https://www.home-assistant.io/docs/mqtt/discovery/)
* Adds **unwrapping**-feature to pushes

**0.12.0**

* Adds additional argument **multi** (default False) to **push.mqtt.MQTTPush** to send multiple messages to the broker if the payload is a dictionary (see plugin docs for reference)
* Adds plugin **pull.monitor.Stats** to periodically emit stats about the host system
* Adds plugin **push.notify.Pushbullet** to send message via the **pushbullet** service
* Adds plugin **push.storage.Dropbox** to upload files to a **dropbox** account/app
* Adds feature to use complex lists and/or dictionary constructs in selector expressions
* Adds plugin **pull.gpio.Watcher** (extra **gpio**) to watch gpio pins for state changes. Only works on raspberry
* Adds plugin **push.simple.Execute** to run commands in a shell
* Adds extra **http-server** to optionally install **flask** and **gevent** when needed
* Adds utility method to check for installed extras
* Adds **-v | --verbose** flag to pnp runner to switch logging level to **DEBUG**. No matter what...

**0.11.3**

* Adds auto-mapping magic to the **pull.zway.ZwayReceiver**.
* Adds humidity and temperature offset to dht

**0.11.2**

* Fixes error catching of **run_pending** in **Polling** base class

**0.11.1**

* Fixes resolution of logging configuration on startup

**0.11.0**

* Introduces the pull.zway.ZwayReceiver and pull.sensor.OpenWeather component
* Introduces logging configurations. Integrates dictmentor package to augment configuration

**0.10.0**

* Introduces engines. You are not enforced to explicitly use one and backward compatibility with legacy configs is given (actually the example configs work as they did before the change). So there shouldn't be any **Breaking** change.
