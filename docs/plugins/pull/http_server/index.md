# pnp.plugins.pull.http.Server

Listens on the specified `port` for requests to any endpoint.
Any data passed to the endpoint will be tried to be parsed to a dictionary (json). If this is not possible
the data will be passed as is. See sections `Result` for specific payload and examples.

Remark: You will not able to make requests to the endpoint DELETE `/_shutdown` because it is used internally.

__Arguments__

**port (int, optional)**: The port the rest server should listen to for requests. Default is 5000.<br/>
**allowed_methods (str or list, optional)**: List of http methods that are allowed. Default is 'GET'.<br/>
**server_impl (str, optional)**: Choose the implementation of the WSGI-Server (wraps the flask-app).
    Possible values are: [flask, gevent]. `flask` uses the internal Flask Development server. Not recommended for
    production use. `gevent` uses [gevent](http://www.gevent.org/). Default is `gevent`.

__Result__

```shell
curl -X GET 'http://localhost:5000/resource/endpoint?foo=bar&bar=baz' --data '{"baz": "bar"}'
```

```yaml
{
    'endpoint': 'resource/endpoint,
    'method': 'GET',
    'query': {'foo': 'bar', 'bar': 'baz'},
    'data': {'baz': 'bar'},
    'is_json': True
}
```

```shell
curl -X GET 'http://localhost:5000/resource/endpoint' --data 'no json obviously'
```

```yaml
{
    'endpoint': 'resource/endpoint,
    'method': 'GET',
    'query': {},
    'data': b'no json obviously',
    'is_json': False
}
```

__Examples__

```yaml
- name: rest
  pull:
    plugin: pnp.plugins.pull.http.Server
    args:
      port: 5000
      allowed_methods: [GET, POST]
  push:
    plugin: pnp.plugins.push.simple.Echo
```
