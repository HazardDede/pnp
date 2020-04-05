# pnp.plugins.pull.net.SSLVerify

Periodically checks if the ssl certificate of a given host is valid and how
many days are remaining before the certificate will expire.

__Arguments__

- **host (str)**: The host
- **timeout (float, optional)**: Timeout for remote checking. Default is 3 seconds.

__Result__

```python
{
    # Envelope
    "host": "www.google.de",
    "payload": {
        "expires_days": 50,  # Remaining days before expiration
        "expires_at": datetime.datetime(2020, 5, 26, 9, 45, 52),  # Python datetime of expiration
        "expired": False  # True of the certificate is expired; otherwise False.
    }
}
```

__Examples__

```yaml
- name: ssl_verify
  pull:
    plugin: pnp.plugins.pull.net.SSLVerify
    args:
      host: www.google.com  # Check the ssl certificate for this host
      interval: 1m  # Check the ssl certificate every minute
      instant_run: true  # ... and run as soon as pnp starts
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
