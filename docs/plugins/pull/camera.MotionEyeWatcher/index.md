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
  source: "abs/path/to/the/image/file.jpg"
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
      path: "{{env::MOTIONEYE_MEDIA_PATH}}"
      image_ext: jpg
      movie_ext: mp4
      motion_cool_down: 30s
      defer_modified: 5
  push:
    plugin: pnp.plugins.push.simple.Echo

```

```yaml
# Publishes a binary motion sensor to home assistant via mqtt discovery  ...
# ... and uploads movies to dropbox when nobody is home and motion is detected
# ... and publishes images to home assistant by a push camera

# Make sure to set the following env vars correctly:
# - MOTIONEYE_MEDIA_PATH: The path where motioneye puts the media files
# - MQTT_HOST: Your mqtt host
# - HA_HOST: Your home assistant url (incl. port)
# - HA_TOKEN: Your home assistant long lived access token
# - DROPBOX_API_KEY: Your dropbox api key
# - PUSHBULLET_API_KEY: Your pushbullet api key

udfs:
  # Defines the udf. name is the actual alias you can call in selector
  # expressions.
  # For fetching the entity of binary_sensor.somebpody_home
  - name: hass_state
    plugin: pnp.plugins.udf.hass.State
    args:
      url: "{{env::HA_URL}}"
      token: "{{env::HA_TOKEN}}"
tasks:
  # Emits events when motioneye creates / modifies image and/or movie files
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
      # Handle motion event
      # - Push on/off to mqtt for automatic home asisstant discovery
      - plugin: pnp.plugins.push.simple.Nop
        selector: "data.state if data.event == 'motion' else SUPPRESS"
        deps:
          - plugin: pnp.plugins.push.mqtt.Discovery
            selector:
              data: "lambda data: data"
              object_id: "motion01_motion"
            args:
              host: "{{env::MQTT_HOST}}"
              discovery_prefix: homeassistant
              component: binary_sensor
              config:
                name: "{{var::object_id}}"
                device_class: "motion"
                payload_on: "on"
                payload_off: "off"
      # Handle image event
      # - Push image to home assistant push camera via url
      - plugin: pnp.plugins.push.simple.Nop
        selector: "data if data.event == 'image' else SUPPRESS"
        deps:
          - plugin: pnp.plugins.push.simple.Execute
            selector:
              data:
              args:
                - "lambda data: data.source"
            args:
              command: ./push_camera.sh
              timeout: 10s
              capture: true
            deps:
              plugin: pnp.plugins.push.simple.Echo
      # Handle movie event
      # - Push movie to dropbox and notify by pushbullet, but only when nobody is home
      - plugin: pnp.plugins.push.simple.Nop
        selector: "data if data.event == 'movie' and hass_state('binary_sensor.somebody_home') == 'off' else SUPPRESS"
        deps:
          - plugin: pnp.plugins.push.storage.Dropbox
            selector:
              data: "lambda data: data.source"
              target_file_name: "lambda data: basename(data.source)"
            deps:
              - plugin: pnp.plugins.push.notify.Pushbullet
                selector: data.raw_link

```

```bash
#!/bin/bash

# Contents of push_camera.sh

IMAGE_FILE=$1

curl -X POST -F "image=@${IMAGE_FILE}" ${HA_HOST}/api/webhook/motion01
```
