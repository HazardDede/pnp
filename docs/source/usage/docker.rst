Docker
======

Prelude
-------

Each new version of **pnp** will also provide a new docker image.

.. code-block::

   # Run your container interactive and delete it after use
   docker run -it --rm -v <path/to/config.yaml>:/config/config.yaml hazard/pnp:latest

   # -d will run the container as a daemon in the background
   docker run -d -v <path/to/config.yaml>:/config/config.yaml hazard/pnp:latest

The image tag ``latest`` points to the latest release. You are encouraged to point to a specific tag.


Use a specific tag
------------------

To use a specific docker image tag you need to replace latest by some valid tag.
By default every version gets its own tag.

For example if you want to use pnp version **0.21.0**

.. code-block::

   docker run -it --rm -v <path/to/config.yaml>:/config/config.yaml hazard/pnp:0.21.0

You can also checkout the Dockerhub_ for available image tags. You will also find **arm**
images to run pnp on a raspberry (which is what I do primarily).

Mounting a config directory
---------------------------

Sometimes you need to add **auxiliary files** like a logging configuration, authentication tokens, dictmentor resources, ....
To make this possible you can mount a directory instead of just a single configuration file.

.. code-block::

   docker run -it --rm -v <path/to/folder:/config hazard/pnp:0.21.0


If you do it this way your main configuration has to be named ``config.yaml``.


.. _Dockerhub: https://hub.docker.com/r/hazard/pnp