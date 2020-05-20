# Features

1\.  [API (0.24.0+)](#api0.24.0+)  

<a name="api0.24.0+"></a>

## 1\. API (0.24.0+)

TBD

* Swagger
* Health
* Prometheus compatible /metrics endpoint

```yaml
api:
  port: 9090  # API listens on port 9090; mandatory
  endpoints:  # Optional
    swagger: true  # Enable swagger endpoint: http://localhost:9090/swagger, default is false.
    metrics: true  # Enable metrics endpoint: http://localhost:9090/metrics, default is false.
tasks:
  - name: api
    pull:
      plugin: pnp.plugins.pull.monitor.Stats
      args:
        instant_run: true
        interval: 1m
    push:
      - plugin: pnp.plugins.push.simple.Echo

```
