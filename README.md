# Pull 'n' Push

[![Python](https://img.shields.io/badge/Python-3.5%20%7C%203.6%20%7C%203.7-green.svg)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/pnp.svg)](https://badge.fury.io/py/pnp)
[![Docs](https://readthedocs.org/projects/pnp/badge/?version=stable)](https://pnp.readthedocs.io/en/stable/?badge=stable)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/HazardDede/pnp.svg)](https://github.com/HazardDede/pnp/commits/master)
[![Build Status](https://travis-ci.org/HazardDede/pnp.svg?branch=master)](https://travis-ci.org/HazardDede/pnp)
[![Coverage Status](https://coveralls.io/repos/github/HazardDede/pnp/badge.svg?branch=master)](https://coveralls.io/github/HazardDede/pnp?branch=master)
[![Docker: hub](https://img.shields.io/badge/docker-hub-brightgreen.svg)](https://cloud.docker.com/u/hazard/repository/docker/hazard/pnp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Project Maintenance](https://img.shields.io/badge/maintainer-Dennis%20Muth%20%40HazardDede-blue.svg)

> Pulls data from sources and pushes it to sinks with optional transformations in between.

## Installation

    pip install pnp

Installation with extras:
    
    pip install pnp[fswatcher,faceR]

Please consult the [component documentation](https://pnp.readthedocs.io/en/stable/plugins/index.html) to see if a
component requires an extra or not.

## Getting started

Define `pulls` to fetch / pull data from source systems.
Define one `push` or multiple `pushes` per pull to transfer the pulled data anywhere else (you only need a plugin that 
knows how to handle the target). You configure your pipeline in `yaml`:

```yaml
tasks:
  - name: hello-world
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        interval: 1s
        repeat: "Hello World"
    push:
      - plugin: pnp.plugins.push.simple.Echo
```
        
Copy this configuration and create the file `helloworld.yaml`. Run it:

    pnp helloworld.yaml

This example yields the string `Hello World` every second.

**Hint**: You can validate your config without actually executing it with

```bash
   pnp --check helloworld.yaml
```

If you want to learn more please see the documentation at [Read the Docs](https://pnp.readthedocs.io/en/stable/).
