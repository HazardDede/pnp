fitbit.Goal
^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.fitbit.Goal     poll   fitbit       0.13.0
================================ ====== ============ ========

**Description**

Requests your goals (water, steps, ...) from the fitbit api.

Please see `Fitbit Authentication`_ to configure to prepare your account accordingly.

**Arguments**

+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
| name      | type      | opt. | default | description                                                                                                                               |
+===========+===========+======+=========+===========================================================================================================================================+
| config    | str       | no   | n/a     | The configuration file that keeps your initial and refreshed authentication tokens (see `Fitbit Authentication`_ for detailed information)|
+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
| resources | List[str] | no   | n/a     | The resources to request (see below for possible options)                                                                                 |
+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
| system    | str       | yes  | None    | The goals to request (see below for detailed information)                                                                                 |
+-----------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+

.. NOTE::

   You can query the following resources:

   * body/fat
   * body/weight
   * activities/daily/activeMinutes
   * activities/daily/caloriesOut
   * activities/daily/distance
   * activities/daily/floors
   * activities/daily/steps
   * activities/weekly/distance
   * activities/weekly/floors
   * activities/weekly/steps
   * foods/calories
   * foods/water

**Result**

Emits a map structure that consists of the requested goals:


.. code-block:: python

   {
     "body/fat": 15.0,
     "body/weight": 70.0,
     "activities/daily/active_minutes": 30,
     "activities/daily/calories_out": 2100,
     "activities/daily/distance": 5.0,
     "activities/daily/floors": 10,
     "activities/daily/steps": 6000,
     "activities/weekly/distance": 5.0,
     "activities/weekly/floors": 10.0,
     "activities/weekly/steps": 6000.0,
     "foods/calories": 2220,
     "foods/water": 1893
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/fitbit.Goal/example.yaml
   :language: YAML