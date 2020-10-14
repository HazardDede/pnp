Installation
============

Installation is done by pip. Simple and straightforward::

    pip install pnp

Some plugins might require some extras to work properly. Installation of extras is simple as well.

Example: The plugin ``pnp.plugins.pull.fitbit.Current`` requires the extra ``fitbit``. To install the extra::

    pip install pnp[fitbit]

If you need to install multiple extras::

    pip install pnp[extra1,extra2,extra3]


Please consult the plugin documentation to see if a component requires an extra or not.

.. IMPORTANT::
   We cannot ensure not to introduce any breaking changes to interfaces / behaviour.
   This might occur every commit whether it is intended or by accident.
   Nevertheless we try to list breaking changes in the changelog that we are aware of.

   You are encouraged to specify the version explicitly in your dependency tools, e.g.::

       pip install pnp==0.23.0

.. WARNING::
   It seems that the package uvloop has some issues on **debian / raspbian stretch**.
   pnp can run without uvloop but sanic installs it as a dependency anyways (but it is optional in our case).
   Unfortunately we can't simply **not** install uvloop in the first place because of
   pnp's package locking mechanism powered by poetry. As far as I can tell there
   is no way to instruct poetry to inject the necessary environment variable to tell
   sanic **not** to install uvloop.
   See the `sanic documentation <https://sanic.readthedocs.io/en/latest/sanic/getting_started.html#install-sanic>`_ for more details.

   **In short**: If you experience segmentation faults after running pnp you should consider to
   remove uvloop from your site-packages.::

       pip uninstall uvloop

