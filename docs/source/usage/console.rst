Console Runner
==============

If you install `pnp` via `pip` it will automatically install a script you can invoke:

.. code-block:: text

    > pnp --help
    Usage: pnp [OPTIONS] CONFIGFILE

      Pull 'n' Push. Runs or checks the given CONFIGFILE

    Options:
      -c, --check                     Only check the given config file but does
                                      not run it.

      --no-log-probe                  Disables the automatic logging configuration
                                      probing.

      --log FILE                      Specify logging configuration to load.
      --log-level [DEBUG|INFO|WARNING|ERROR]
                                      Overrides the log level.
      --version                       Show the version and exit.
      --help                          Show this message and exit.

Alternatively you can call the module via python interpreter:

.. code-block:: bash

   python3 -m pnp --help