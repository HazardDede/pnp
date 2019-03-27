# pnp.plugins.pull.simple.Cron

Execute push-components based on time constraints configured by cron-like expressions.

This plugin basically wraps [cronex](https://pypi.org/project/cronex/) to parse cron expressions and to check if
any job is pending. See the documentation of `cronex` for a guide on featured/supported cron expressions.

__Arguments__

- **exppresions (List[str])**: Cron like expressions to configure the scheduler.

__Result__

Imagine your cron expressions looks like this: `*/1 * * * * every minute`.
The pull will emit every minute the same payload:

```yaml
{
  'data': 'every minute'
}
```

__Examples__

```yaml
- name: cron
  pull:
    plugin: pnp.plugins.pull.simple.Cron
    args:
      expressions:
        - "*/1 * * * * every minute"
        - "0 15 * * * 3pm"
        - "0 0 * * * midnight every day"
        - "0 16 * * 1-5 every weekday @ 4pm"
  push:
    plugin: pnp.plugins.push.simple.Echo

```
