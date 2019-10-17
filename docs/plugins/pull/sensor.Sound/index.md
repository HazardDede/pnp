# pnp.plugins.pull.sensor.Sound

Listens to the microphone in realtime and searches the stream for specific sound patterns.
Practical example: I use this plugin to recognize my doorbell without tampering with the electrical device ;-)

Requires extra `sound`.

__Arguments__

- **wav_files (List[Dict])**: A list of dictionaries containing the configuration for each file that contains an original sound pattern to listen for.
The configuration consists of the following keys:
    * **path (str)**: The path to the original sound file. Absolute or relative to the pnp configuration file
    * **mode (Union[pearson,std], optional)**: Correlation/similarity method. Default is pearson. Try out which one is best for you
    * **offset (float, optional)**: Adjusts sensitivity for similarity
Positive means less sensitive; negative is more sensitive. You should try out 0.1 steps. Default is 0.0
    * **offset (dict, optional)**: Contains the cooldown configuration. Default is a cooldown period of 10 seconds and no emit of a cooldown event
        - **period (duration, optional)**: Prevents the pull to emit more than one sound detection event per cool down period. Default is 10 seconds
        - **emit_event (bool, optional)**: If set to true the end of the cooldown period will an emit as well. Default is false
- **device_index (int, optional)**: The index of the microphone device. Run `pnp_record_sound --list` to get the index.
If not specified pyAudio will try to find a capable device
- **ignore_overflow (bool, optional)**: If set to True any buffer overflows due to slow realtime processing will be ignored.
    Otherwise an exception will be thrown

Hints:
* You can list your available input devices: `pnp_record_sound --list`
* You can record a wav file from an input device: `pnp_record_sound <out.wav> <seconds_to_record> --index=<idx>`
* This one is _not_ pre-installed when using the docker image. Would be grateful if anyone can integrate it


__Result__

Will emit the event below when the correlation coefficient is above or equal the threshold.
In this case the component has detected a sound that is similar to one of the given sound patterns

```yaml
{
    "type": "sound"  # Type 'sound' means we detected a sound pattern
    "sound": ding,  # Name of the wav_file without path and extension. To differentiate if you have multiple patterns you listen to
    "corrcoef": 0.82,  # Correlation coefficient probably between [-1;+1] for pearson
    "threshold": 0.6  # Threshold influenced by sensitivity_offset
}
```

Will emit the event below when you have configured the component to send cooldown events as well.

```yaml
{
    "type": "cooldown"  # Type 'cooldown' means that we previously identified a sound pattern and the cooldown has happened
    "sound": ding,  # Name of the wav_file without path and extension. To differentiate if you have multiple patterns you listen to
}
```

__Examples__

```yaml
- name: sound_detector
  pull:
    plugin: pnp.plugins.pull.sensor.Sound
    args:
      wav_files:  # The files to compare for similarity
        - path: ding.wav  # Absolute or relative (from the config) path to the wav file
          mode: std  # Use std correlation coefficient [pearson, std]; optional default is pearson
          offset: -0.5  # Adjust sensitivity. Positive means less sensitive; negative is more sensitive. Default is 0.0
        - path: doorbell.wav  # This will use default values for mode and offset (pearson, 0.0)
          cooldown:
            period: 10s  # Prevents the pull to emit more than one sound detection event every 10 seconds
            emit_event: true  # Fire an event after the actual cool down - Useful for binary_sensors to return to their 'off' state
      device_index:  # The index of the microphone devices. If not specified pyAudio will try to find a capable device
      ignore_overflow: true  # Some devices might be too slow to process the stream in realtime. Ignore any buffer overflow errors.
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
