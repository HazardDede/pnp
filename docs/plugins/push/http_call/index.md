# pnp.plugins.push.http.Call

Makes a request to a http resource.

__Arguments__

**url (str)**: Request url. Can be overridden via envelope.<br/>
**method (str, optional)**: The http method to use for the request. Must be a valid http method (GET, POST, ...).
    Default is 'GET'. Can be overridden via envelope.<br/>
**fail_on_error (bool, optional)**: If True the push will fail on a http status code <> 2xx. This leads to an error
    message recorded into the logs and no further execution of any dependencies. Default is False. Can be overridden
    by the envelope.<br/>
**provide_response (bool, optional)**: If True the push will _not_ return the payload as it is, but instead provide the
    response status_code, fetched url content and a flag if the url content is a json response. This is useful for
    other push instances in the dependency chain. Default is False.

__Result__

Will return the payload as it is for easy chaining of dependencies.
If `provide_response` is True the push will return a dictionary that looks like this:

```yaml
{
    "status_code": 200,
    "data": "fetched url content",
    "is_json": False
}
```

Please note that this structure will be interpreted as an envelope with the keys `status_code` and `is_json` along with
the payload 'fetched url content' by other push instances in the dependency chain.

__Examples__

```yaml
# Simple example calling the built-in rest server
# Oscillates between http method GET and POST. Depending on the fact if the counter is even or not.
- name: http_call
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 5
  push:
    plugin: pnp.plugins.push.http.Call
    selector: "dict(data=dict(counter=payload), method='POST' if int(payload) % 2 == 0 else 'GET')"
    args:
      url: http://localhost:5000/
- name: rest_server
  pull:
    plugin: pnp.plugins.pull.http.Server
    args:
      port: 5000
      allowed_methods:
        - GET
        - POST
  push:
    plugin: pnp.plugins.push.simple.Echo
```

```yaml
# Demonstrates the use of `provide_response` set to True.
# Call will return a response object to dependent push instances.
- name: http_call
  pull:
    plugin: pnp.plugins.pull.simple.Count
    args:
      wait: 5
  push:
    plugin: pnp.plugins.push.http.Call
    args:
      url: http://localhost:5000/
      provide_response: True
    deps:
      plugin: pnp.plugins.push.simple.Echo
- name: rest_server
  pull:
    plugin: pnp.plugins.pull.http.Server
    args:
      port: 5000
      allowed_methods:
        - GET
  push:
    plugin: pnp.plugins.push.simple.Nop
```
