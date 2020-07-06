sensor.OpenWeather
^^^^^^^^^^^^^^^^^^

==================================== ====== ============ ========
plugin                               type   extra        version
==================================== ====== ============ ========
pnp.plugins.pull.sensor.OpenWeather  poll   none         0.11.0
==================================== ====== ============ ========

**Description**

Periodically polls weather data from the ``OpenWeatherMap`` api.

**Arguments**

+-----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------+
| name      | type  | opt. | default | description                                                                                                                       |
+===========+=======+======+=========+===================================================================================================================================+
| api_key   | str   | no   | n/a     | The api_key you got from OpenWeatherMap after registration.                                                                       |
+-----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------+
| lat       | float | yes  | None    | Latitude. If you pass ``lat``, you have to pass ``lon`` as well.                                                                  |
+-----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------+
| lon       | float | yes  | None    | Longitude. If you pass ``lon``, you have to pass ``lat`` as well.                                                                 |
+-----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------+
| city_name | str   | yes  | None    | The name of your city. To minimize ambiguity use lat/lon or your country as a suffix, e.g. London,GB.                             |
+-----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------+
| units     | str   | yes  | metric  | Specify units for temperature and speed. imperial = fahrenheit + miles/hour, metric = celsius + m/secs, kelvin = kelvin + m/secs. |
+-----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------+
| tz        | str   | yes  | None    | Time zone to use for current time and last updated time. Default is your local timezone.                                          |
+-----------+-------+------+---------+-----------------------------------------------------------------------------------------------------------------------------------+

.. NOTE::

   You have to pass whether ``city_name`` or ``lat/lon``.

**Result**

Emits a dictionary that contains an entry for every sensor of the plant sensor device:


.. code-block:: python

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

**Example**

.. literalinclude:: ../code-samples/plugins/pull/sensor.OpenWeather/example.yaml
   :language: YAML