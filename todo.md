# Open tasks

## General

* Documentation
* Tests ;-)
* Dockerfile for raspi and other (done)
* Make resolver are self-maintained repository
* Better argument parsing via docopt (or similar)
* Join for workers. Not easy cause last worker will leave a message on the queue
* Overview on startup on configured tasks (done)
* Rest-Api to watch various things
* Rename inbound/outbound to pull/push (backward compatibility) (done)
* Makefile (done)
* Versionbump - Release process (done)

## Plugins

* Better error message when no resolution via envargs was not possible (hint of the environment variable to set)
* Push: Extract timestamp and queue as well
* Influx: Use timestamp from queue not actual one (value might be measured long before - depends on how many queue items are queued up already)
* Detect hanging plugins / restart broken plugins
* Make logging easier

## Helpful Doc

https://packaging.python.org/tutorials/distributing-packages/
http://docs.python-guide.org/en/latest/writing/structure/