# pnp.plugins.pull.http.Server

Creates a specific route on the builtin api server and listens to any call to that route.
Any data passed to the endpoint will be tried to be parsed to a dictionary (json).
If this is not possible the data will be passed as is. See sections `Result` for specific payload and examples.

You need to enable the api via configuration to make this work.

__Arguments__

- **prefix_path (str)**: The route to create for incoming traffic on the builtin api server. See the Example section for reference.
- **allowed_methods (str or list, optional)**: List of http methods that are allowed. Default is 'GET'.

__Result__

Assumes that you configured your pull with `prefix_path = callme`

```bash
curl -X GET "http://localhost:9999/callme/telephone/now?number=12345&priority=high" --data '{"magic": 42}'
```

```json
{
  "endpoint": "telephone/now",
  "data": {"magic": 42},
  "levels": ["telephone", "now"],
  "method": "GET",
  "query": {"number": "12345", "priority": "high"},
  "is_json": True,
  "url": "http://localhost:9999/callme/telephone/now?number=12345&priority=high",
  "full_path": "/callme/telephone/now?number=12345&priority=high",
  "path": "/callme/telephone/now"
}
```

__Examples__

```yaml
#
# Registers the endpoint /callme to the builtin api server.
# Use curl to try it out:
#   curl -X GET "http://localhost:9999/callme/telephone/now?number=12345&priority=high" --data '{"magic": 42}'
#

api:  # You need to enable the api
  port: 9999  # Mandatory
tasks:
  - name: server
    pull:
      plugin: pnp.plugins.pull.http.Server
      args:
        prefix_path: callme  # Results into http://localhost:9999/callme
        allowed_methods:  # Specify which methods are allowed
          - GET
          - POST
    push:
      plugin: pnp.plugins.push.simple.Echo

```
