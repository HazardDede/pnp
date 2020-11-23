Plugins
=======

Pulls
-----

Pulls can be divided into pulls that react on events and pulls that regularly poll for data.

So called ``Polling`` components are special ``pulls`` that - as stated earlier - regularly poll data or just execute
in regular intervals.

Besides the arguments stated in the component description ``polls`` always have the following
arguments to control their polling behavior.

+-------------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name        | type      | opt. | default | description                                                                                                                                                                                           |
+=============+===========+======+=========+=======================================================================================================================================================================================================+
| interval    | str/float | yes  | 60s     | You may specify duration literals such as ``60`` (60 secs), ``1m``, ``1h`` (...) to realize a periodic polling or cron expressions e.g. ``*/1 * * * *`` (every minute) to realize cron like behavior. |
+-------------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| instant_run | bool      | yes  | False   | If set to True the component will run as soon as ``pnp`` starts; otherwise it will run the next configured interval.                                                                                  |
+-------------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. include:: pull/camera.MotionEyeWatcher.rst

.. include:: pull/fitbit.Current.rst

.. include:: pull/fitbit.Devices.rst

.. include:: pull/fitbit.Goal.rst

.. include:: pull/fs.FileSystemWatcher.rst

.. include:: pull/fs.Size.rst

.. include:: pull/ftp.Server.rst

.. include:: pull/gpio.Watcher.rst

.. include:: pull/hass.State.rst

.. include:: pull/http.Server.rst

.. include:: pull/monitor.Stats.rst

.. include:: pull/mqtt.Subscribe.rst

.. include:: pull/net.PortProbe.rst

.. include:: pull/net.Speedtest.rst

.. include:: pull/net.SSLVerify.rst

.. include:: pull/presence.FritzBoxTracker.rst

.. include:: pull/sensor.DHT.rst

.. include:: pull/sensor.MiFlora.rst

.. include:: pull/sensor.OpenWeather.rst

.. include:: pull/sensor.Sound.rst

.. include:: pull/simple.Count.rst

.. include:: pull/simple.Cron.rst

.. include:: pull/simple.Repeat.rst

.. include:: pull/simple.RunOnce.rst

.. include:: pull/traffic.DeutscheBahn.rst

.. include:: pull/zway.ZwayPoll.rst


Pushes
------

Like a ``pull`` a ``push`` does support ``args`` to initialize the instance of a ``push``.
Besides that you can optionally pass a ``selector`` to transform the incoming payload
and set the ``unwrap`` option to invoke a ``push`` for each element of an ``iterable``.

.. seealso::

   Some ``pushes`` do support the ``envelope`` feature to alter the arguments for a ``push`` during
   runtime: :ref:`Envelope <blocks_envelope>`

.. include:: push/fs.FileDump.rst

.. include:: push/fs.Zipper.rst

.. include:: push/hass.Service.rst

.. include:: push/http.Call.rst

.. include:: push/ml.FaceR.rst

.. include:: push/mqtt.Discovery.rst

.. include:: push/mqtt.Publish.rst

.. include:: push/notify.Slack.rst

.. include:: push/simple.Echo.rst

.. include:: push/simple.Execute.rst

.. include:: push/simple.Nop.rst

.. include:: push/simple.Wait.rst

.. include:: push/storage.Dropbox.rst

.. include:: push/timedb.InfluxPush.rst

UDFs
----

.. versionadded:: 0.14.0

All udfs do share the following base arguments:

+----------+-----------+------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
| name     | type      | opt. | default | description                                                                                                                            |
+==========+===========+======+=========+========================================================================================================================================+
| throttle | str/float | yes  | None    | If set to a valid duration literal (e.g. ``5m``) the return value of the called functions will be cached for the given amount of time. |
+----------+-----------+------+---------+----------------------------------------------------------------------------------------------------------------------------------------+

.. include:: udf/hass.State.rst

.. include:: udf/simple.Counter.rst

.. include:: udf/simple.FormatSize.rst

.. include:: udf/simple.Memory.rst

Appendix
--------

.. include:: appendix/gmail_token.rst

.. include:: appendix/fitbit_auth.rst
