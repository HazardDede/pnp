Quickstart
==========

The major concepts of Pull 'n' Push are **pulls** and **pushes** (surprise!).

**Pulls** define how to fetch data from sources.
A pull passes it's fetched data to one or more **push** components.

.. NOTE::
    Example: The pull ``pnp.plugins.pull.monitor.Stats`` periodically fetches statistics
    from the host it is running on (like cpu and ram usage).
    It passes it's statistics on to the ``pnp.plugins.push.mqtt.Publish`` to
    publish those statistics on a mqtt broker.

Gluing together pulls and pushes is done by a **task**. It's similar to defining an input / output pipeline.

Now let's get serious. Copy and paste the following configuration to the file ``helloworld.yaml``.

.. literalinclude:: ../code-samples/quickstart/helloworld.yaml
   :language: YAML

And run it by invoking the console runner::

    pnp helloworld.yaml

This example yields the string ``'Hello World'`` every second.