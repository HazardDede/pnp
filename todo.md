# Open tasks

## General

* Documentation
* Tests ;-)
* Dockerfile for raspi and other
* Make resolver are self-maintained repository
* Better argument parsing via docopt (or similiar)

## Plugins

* Better error message when no resolution via envargs was possible (hint of the environment variable to set)
* Push: Extract timestamp and queue as well
* Influx: Use timestamp from queue not actual one (value might be measured long before - depends on how many queue items are queued up already)

## Helpful Doc

https://packaging.python.org/tutorials/distributing-packages/