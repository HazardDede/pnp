gpio.Watcher
^^^^^^^^^^^^

================================ ====== ============ ========
plugin                           type   extra        version
================================ ====== ============ ========
pnp.plugins.pull.gpio.Watcher    poll   gpio         0.12.0
================================ ====== ============ ========

**Description**

Listens for low/high state changes on the configured gpio pins.

In more detail the plugin can raise events when one of the following situations occur:

* **rising (high)** of a gpio pin - multiple events may occur in a short period of time
* **falling (low)** of a gpio pin - multiple events may occur in a short period of time
* **switch** of gpio pin - will suppress multiple events a defined period of time (bounce time)
* **motion** of gpio pin - will raise the event `motion_on` if the pin rises and set a timer with a configurable amount of
  time. Any other gpio rising events will reset the timer. When the timer expires the `motion_off` event is raised.


**Arguments**

+---------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name    | type      | opt. | default | description                                                                                                                                                       |
+=========+===========+======+=========+===================================================================================================================================================================+
| pins    | List[int] | no   | n/a     | The gpio pins to observe for state changes. Please see the examples section on how to configure it.                                                               |
+---------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| default | str       | no   | n/a     | The default edge that is applied when not configured. Please see the examples section for further details. One of ``rising``, ``falling``, ``switch``, ``motion`` |
+---------+-----------+------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Result**

Emits a dictionary that contains an entry for every sensor of the plant sensor device:


.. code-block:: python

   {
     "gpio_pin": 17  # The gpio pin which state has changed
     "event": rising  # One of [rising, falling, switch, motion_on, motion_off]
   }

**Example**

.. literalinclude:: ../code-samples/plugins/pull/gpio.Watcher/example.yaml
   :language: YAML