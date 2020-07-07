Building Blocks
===============

Pull
----

The **pull** is the primary building block when it comes down to fetching / retrieving data from
various sources.

Some examples:

* Start up a FTP server and wait for new uploaded files
* Listen to created, updated or deleted files in the file system
* Listen to a mqtt broker for new messages on a specific topic
* Frequently poll the fitbit api to fetch the current step count
* Frequently poll the host for statistics (like cpu / ram usage)
* ...

As you can see pulls can either

* **react** on one or multiple events (like files created, updated, deleted)
* or frequently **poll** a source

to provide data to its downstream: the **push**

.. literalinclude:: ../code-samples/building-blocks/pull.yaml
   :language: YAML

Push
----

A **push** simply processes the downstream data from a pull.

Some examples:

* Publish a message on a specific topic on an mqtt broker
* Send a templated notification via slack
* Execute a script using derived arguments
* Send a http request to a server
* Simply echo the data to the console (nice for debugging)
* ...

.. literalinclude:: ../code-samples/building-blocks/push.yaml
   :language: YAML

Selector
--------

Sometimes the output of a pull needs to be **transformed** before the downstream push can handle it.
**Selectors** to the rescue: A selector transforms the output of a pull by using pure python code.

.. literalinclude:: ../code-samples/building-blocks/selector.yaml
   :language: YAML

Easy as that. We can reference our incoming data via **data** or **payload**.

.. seealso:: :ref:`Advanced Selector Expression <advanced_selector>`

Dependencies
------------

By default all defined pushes will execute in parallel when new incoming data is available.
But now it would be awesome if we could **chain** pushes together.
So that the **output** of one push becomes the **input** of the next push.
The good thing is: Yes we can.

.. literalinclude:: ../code-samples/building-blocks/dependencies.yaml
   :language: YAML

.. _blocks_envelope:

Envelope
--------

.. versionadded:: 0.7.0

By using an **envelope** it is possible to change the behavior of pushes **during runtime**.
One of the best examples is **pnp.plugins.push.mqtt.Publish** plugins where you can override the actual topic where the message should be published.

Easier to understand by a practical example:

.. literalinclude:: ../code-samples/building-blocks/envelope.yaml
   :language: YAML

**How does this work**

If the emitted or transformed payload (via selector) contains the key **data** or **payload** the pipeline assumes that
this is the actual payload and all other keys represent the so called **envelope**.

.. note::

   It is easy to construct envelopes by using the :ref:`Advanced Selector Expression <advanced_selector>`

UDFs
----

.. versionadded:: 0.14.0

When transforming the output of a pull with the help of a selector you sometimes need to call
python functions to perform certain operations. A selector does only provide very few basic functions like
type conversions (``str``, ``float``, ...) out of the box.

But the good thing is: You can register simple python builtin functions, special user defined functions and your
own python functions to make use of them.

Besides providing function logic UDFs can carry a state and some special behavior like out of the box throttling.

.. literalinclude:: ../code-samples/building-blocks/udf.yaml
   :language: YAML

.. seealso:: :ref:`UDF throttle <udf_throttle>`