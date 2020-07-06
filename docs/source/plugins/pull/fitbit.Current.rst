fitbit.Current
^^^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.fitbit.Current  poll   fitbit       0.13.0
================================ ====== ============ ========

**Description**

Requests various current metrics (steps, calories, distance, ...) from the fitbit api for a specific account.

Please see `Fitbit Authentication`_ to configure to prepare your account accordingly.

**Arguments**

+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
| name      | type      | opt. | default | description                                                                                                                               |
+===========+===========+======+=========+===========================================================================================================================================+
| config    | str       | no   | n/a     | The configuration file that keeps your initial and refreshed authentication tokens (see `Fitbit Authentication`_ for detailed information)|
+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
| resources | List[str] | no   | n/a     | The resources to request (see below for possible options)                                                                                 |
+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
| system    | str       | yes  | None    | The metric system to use based on your localisation (de_DE, en_US, ...). Default is your configured metric system in your fitbit account  |
+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+

.. NOTE::

   You can query the following resources:

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

**Result**

Emits a map that contains the requested resources and their associated values:


.. code-block:: python

    {
      "activities/calories": 1216,
      "activities/caloriesBMR": 781,
      "activities/steps": 4048,
      "activities/distance": 3.02385,
      "activities/floors": 4,
      "activities/elevation": 12,
      "activities/minutes_sedentary": 127,
      "activities/minutes_lightly_active": 61,
      "activities/minutes_fairly_active": 8,
      "activities/minutes_very_active": 24,
      "activities/activity_calories": 484,
      "body/bmi": 23.086421966552734,
      "body/fat": 0.0,
      "body/weight": 74.8,
      "foods/log/calories_in": 0,
      "foods/log/water": 0.0,
      "sleep/awakenings_count": 0,
      "sleep/efficiency": 84,
      "sleep/minutes_after_wakeup": 0,
      "sleep/minutes_asleep": 369,
      "sleep/minutes_awake": 69,
      "sleep/minutes_to_fall_asleep": 0,
      "sleep/start_time": "21:50",
      "sleep/time_in_bed": 438
    }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/fitbit.Current/example.yaml
   :language: YAML