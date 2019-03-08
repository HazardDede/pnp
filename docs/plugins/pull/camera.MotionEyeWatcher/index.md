# pnp.plugins.pull.camera.MotionEyeWatcher

Watches a motioneye directory (where the images and the movies get persisted from motioneye) to trigger some useful events
based on new / modified files. The motion event only works, when the camera is configured to persist images / movies
only when motion is triggered and not 24/7.

For example I use this plugin to publish a binary motion sensor via mqtt discovery to home assistant and upload the
images and videos to dropbox and notify me via pushbullet.

Requires extra `fswatcher`.

__Arguments__

- **path (str)**: The motioneye media directory to watch.
- **image_ext (Optional[str])**: The file extension of your image files. Default is 'jpg'. Deactivate with None.
- **movie_ext (Optional[str])**: The file extension of your movie files. Default is 'mp4'. Deactivate with None.
- **motion_cool_down (Optional[bool])**: Based on created/modified files a motion event might be triggered. After the specified time without motion, the `motion off` event will be triggered.
- **defer_modified (float, optional)**: If set greater than 0, it will defer the sending of modified events for that
    amount of time (seconds). There might be multiple flushes of a file before it is written completely to disk.
    Without defer_modified each flush will raise a modified event. Default is 0.5.

__Result__

Example of a new movie file:

```yaml
{
  event: "movie",
  source: "abs/path/to/the/movie/file.mp4"
}
```

Example of a new image file:

```yaml
{
  event: "image",
  source: "abs/path/to/the/image/file.mp4"
}
```

Example of a new motion on/off event:

```yaml
{
  event: "motion",
  state: "on"  # or "off"
}
```

__Examples__

```yaml
# Basic example - just echoing events

- name: motioneye_watcher
  pull:
    plugin: pnp.plugins.pull.camera.MotionEyeWatcher
    args:
      path: "/tmp"
      image_ext: jpg
      movie_ext: mp4
      motion_cool_down: 30s
      defer_modified: 5
  push:
    plugin: pnp.plugins.push.simple.Echo
```

```yaml
# Publishes a binary motion sensor to home assistant via mqtt discovery  ...
# ... and uploads images and movies to dropbox when nobody is home and motion is detected

# Make sure to set the following env vars correctly:
# - MOTIONEYE_MEDIA_PATH: The path where motioneye puts the media files
# - HA_TOKEN: Your home assistant long lived access token
# - DROPBOX_API_KEY: Your dropbox api key
# - PUSHBULLET_API_KEY: Your pushbullet api key

udfs:
- name: hass_state
  plugin: pnp.plugins.udf.hass.State
  args:
    url: http://services:8123
    token: "{{env::HA_TOKEN}}"
tasks:
- name: motioneye_watcher
  pull:
    plugin: pnp.plugins.pull.camera.MotionEyeWatcher
    args:
      path: "{{env::MOTIONEYE_MEDIA_PATH}}"
      image_ext: jpg
      movie_ext: mp4
      motion_cool_down: 30s
      defer_modified: 5
  push:
  - plugin: pnp.plugins.push.simple.Nop
    selector: "data.state if data.event == 'motion' else SUPPRESS"
    deps:
    - plugin: pnp.plugins.push.mqtt.Discovery
      selector:
        data: "lambda data: data"
        object_id: "motion01_motion"
      args:
        host: services
        discovery_prefix: homeassistant
        component: binary_sensor
        config:
          name: "{{var::object_id}}"
          device_class: "motion"
          payload_on: "on"
          payload_off: "off"
  - plugin: pnp.plugins.push.storage.Dropbox
    selector: "dict(data=data.source, target_file_name=basename(data.source)) if data.event in ['image', 'movie'] and hass_state('group.all_devices') == 'not_home' else SUPPRESS"
    args:
      api_key: "{{env::DROPBOX_API_KEY}}"
    deps:
    - plugin: pnp.plugins.push.notify.Pushbullet
      selector: data.raw_link
      args:
        api_key: "{{env::PUSHBULLET_API_KEY}}"
```
