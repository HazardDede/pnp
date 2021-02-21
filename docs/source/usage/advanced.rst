Advanced topics
===============

.. _advanced_selector:

Advanced selector expressions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.12.0

Instead of string-only selector expressions, you may now use complex dictionary
and/or list constructs in your yaml to define a selector expression. If you use
a dictionary or a list make sure to provide "real" selectors as a lambda
expression, so the evaluator can decide if this is a string literal or an
expression to evaluate.

The configuration below will repeat

.. code-block::
   yaml

   {'hello': 'Hello', 'words': ['World', 'Moon', 'Mars']}

.. literalinclude:: ../code-samples/advanced/selector/basic.yaml
   :language: YAML

Prior to the implementation of the advanced selector feature your expressions
would have probably looked similar to this::

   dict(hello=payload.split(' ')[0], words=[payload.split(' ')[1], payload.split(' ')[2], payload.split(' ')[3]])

The first one is more readable, isn't it?

A more complex example showcasing literals and lambda expressions in more depth:

.. literalinclude:: ../code-samples/advanced/selector/complex.yaml
   :language: YAML

API
^^^

.. versionadded:: 0.24.0

You can explicitly activate an rest-api to perform various stuff:

Determine if everything is up and running::

     curl -X GET "http://localhost:9999/health"

Retrieve the current ``python`` and ``pnp`` version::

     curl -X GET "http://localhost:9999/version"

Change the log level at runtime. Useful if you want to track down an issue. Example::

     curl -X POST "http://localhost:9999/loglevel?level=DEBUG"

Retrieve prometheus compliant metrics::

     curl -X GET "http://localhost:9999/metrics"

See the openapi specification in your browser:
`http://localhost:9999/docs <http://localhost:9999/docs>`_

Trigger tasks manually (even when the task has some schedule assigned)::

     curl -X POST "http://localhost:9999/trigger?task=<task_name>"

.. note::

   You need to explicitly enable the ``/metrics`` endpoint while configuring your api.
   Please see the example below for reference.

.. literalinclude:: ../code-samples/advanced/api/example.yaml
   :language: YAML

To create a task with no schedule assigned you can pass ``nothing`` to the ``interval``
argument of your task. This way the task will not be scheduled automatically. The only
way to run it is to do it explicitly via the api.

.. literalinclude:: ../code-samples/advanced/api/trigger.yaml
   :language: YAML

Augment configuration
^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 0.28.0
   Use `YAML Tags`_.
   dictmentor for configuration augmentation will be removed in a future release.

You can augment the configuration by extensions from the ``dictmentor`` package.
Please see `dictmentor on Github <https://github.com/HazardDede/dictmentor>`_ for further reference.

The ``dictmentor`` instance will be instantiated with the following code
and thus the following extensions:

.. code-block::
   python

   from dictmentor import DictMentor, ext
   return DictMentor(
     ext.Environment(fail_on_unset=True),
     ext.ExternalResource(base_path=os.path.dirname(config_path)),
     ext.ExternalYamlResource(base_path=os.path.dirname(config_path))
   )

The following configuration will demonstrate the configuration augmentation in more
depth:

.. literalinclude:: ../code-samples/advanced/dictmentor/base.yaml
   :language: YAML

.. literalinclude:: ../code-samples/advanced/dictmentor/repeat.pull
   :language: YAML

.. literalinclude:: ../code-samples/advanced/dictmentor/echo.push
   :language: YAML

.. literalinclude:: ../code-samples/advanced/dictmentor/nop.push
   :language: YAML

Engines
^^^^^^^

In version ``0.22.0`` I've decided to remove all engines except for the Async engine.
Due to some tests this engine is amazingly stable, has great performance and you do not
need to think about synchronizing parallel tasks so much.

This decision was basically driven from a maintenance view of perspective.
In the future I like to add some infrastructural code like an api to communicate with the engine.
And I will not be able to integrate necessary changes to all of the engines.

By default the ``AsyncEngine`` is used implicitly:

.. literalinclude:: ../code-samples/advanced/engine/implicit.yaml
   :language: YAML

You can add it explicitly though.
This might be useful in the future IF I decide to add variants of the ``AsyncEngine`` or
if you want to use a ``RetryHandler``.

.. literalinclude:: ../code-samples/advanced/engine/explicit.yaml
   :language: YAML

Logging
^^^^^^^

.. versionadded:: 0.11.0

You can use different logging configurations in two ways:
Either by specify the logging configuration when starting ``pnp`` via the console
or by setting the environment variable ``PNP_LOG_CONF`` and then run ``pnp``.

.. code-block:: bash

   # Specify explicitly when starting pnp
   pnp --log=<logging_configuration> <pnp_configuration>

   # Specify by environment variable
   export PNP_LOG_CONF=<logging_configuration>
   pnp <pnp_configuration>

If you do not specify a logging configuration explicitly pnp will search for a ``logging.yaml``
1. in the current working directory
2. in the directory where your pnp configuration file is located

You can disable this automatic and implicit logging configuration probing by starting pnp
by passing ``--no-log-probe``:

.. code-block:: bash

   pnp --no-log-probe <pnp_configuration>


A simple logging configuration that will log severe errors to a separate
rotating log file looks like this:

.. code-block:: yaml

   version: 1
   disable_existing_loggers: False

   formatters:
       simple:
           format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

   handlers:
       console:
           class: logging.StreamHandler
           level: DEBUG
           formatter: simple
           stream: ext://sys.stdout

       error_file_handler:
           class: logging.handlers.RotatingFileHandler
           level: ERROR
           formatter: simple
           filename: errors.log
           maxBytes: 10485760 # 10MB
           backupCount: 20
           encoding: utf8

   root:
       level: INFO
       handlers: [console, error_file_handler]

Payload unwrapping
^^^^^^^^^^^^^^^^^^

Sometimes a ``pull`` returns a list of items or you created a list of readings by
using the ``selector``. As long as a ``push`` can process a list as an input everything
is fine. But now imagine that you want to process each item of that list
individually. ``Unwrapping`` to the rescue. ``Unwrapping`` will exactly allow
you what was asked for above: Pass each item of a list to a ``push`` individually.

.. literalinclude:: ../code-samples/advanced/unwrapping/simple.yaml
   :language: YAML

But sometimes you want to add items to the list before processing it item
by item. You can do this by using a ``push.simple.Nop`` properly.

.. literalinclude:: ../code-samples/advanced/unwrapping/nop.yaml
   :language: YAML

Retry handler
^^^^^^^^^^^^^

By using the explicit form of the engine specification you can specify a so called
``RetryHandler`` as well. A ``RetryHandler`` controls what happens if your ``push``
unexpectedly exits or raises an error.

**NoRetryHandler**

Will not retry ro run the ``pull`` if it fails. If all ``pulls`` exit for some reason
``pnp`` will exit as well.

.. literalinclude:: ../code-samples/advanced/retry_handler/no_retry.yaml
   :language: YAML


**SimpleRetryHandler**

In addition to the ``NoRetryHandler`` this handler will retry after a specified amount of time
configured by passing ``retry_wait`` (default is 60 seconds).

.. literalinclude:: ../code-samples/advanced/retry_handler/simple.yaml
   :language: YAML

**LimitedRetryHandler**

In addition to retrying the ``pull`` you can configure how many retries are allowed by passing
``max_retries`` (default is 3). Each failed ``pull`` execution will raise the counter and
the counter will not reset.

.. literalinclude:: ../code-samples/advanced/retry_handler/limited.yaml
   :language: YAML

**AdvancedRetryHandler**

In addition to the ``LimitedRetryHandler`` the counter will be reset if the ``pull``
has ran successful for a specific amount of time by passing ``reset_retry_threshold``
(default is 60 seconds).

.. literalinclude:: ../code-samples/advanced/retry_handler/advanced.yaml
   :language: YAML

.. note::

   If no ``RetryHandler`` is explicitly specified the ``AdvancedRetryHandler`` will be used.
   The instance created will use the default values for it's arguments.

Suppress push
^^^^^^^^^^^^^

Sometimes you want to suppress (do not execute) a push based on the actual
incoming payload from a ``pull``. To achieve this all you have to do is to
emit the special sentinel ``SUPPRESS`` from your ``selector`` expression.

.. literalinclude:: ../code-samples/advanced/suppress/suppress.yaml
   :language: YAML

.. _udf_throttle:

UDF Throttle
^^^^^^^^^^^^

Consider the following situation: You have a selector that uses a udf to fetch a state from an external system.

The state won't change so often, but your selector will fetch the state every time a pull transports a payload to the push.
You want to decrease the load on the external system and you want to increase throughput.

Throttling to the rescue. Specifying ``throttle`` when instantiating your udf will manage that your udf will only
call the external system once and cache the result. Subsequent calls will either return the cached result or call the
external system again when a specified time has passed since the last call that actually fetched a result from the external
system.

.. literalinclude:: ../code-samples/advanced/udf/udf-throttle.yaml
   :language: YAML

YAML Tags
^^^^^^^^^

You can use yaml tags to augment your yaml configuration.
Right now the following tags are supported:

``!include``: To incorporate another yaml file into your configuration

The following example will demonstrate the yaml tags in more depth:

.. literalinclude:: ../code-samples/advanced/yaml_tags/base.yaml
   :language: YAML

.. literalinclude:: ../code-samples/advanced/yaml_tags/_repeat.yaml
   :language: YAML

.. literalinclude:: ../code-samples/advanced/yaml_tags/_echo.yaml
   :language: YAML

.. literalinclude:: ../code-samples/advanced/yaml_tags/_nop.yaml
   :language: YAML