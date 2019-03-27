# pnp.plugins.pull.sensor.Sound

Listens to the microphone in realtime and searches the stream for a specific sound pattern.
Practical example: I use this plugin to recognize my doorbell without tampering with the electrical device ;-)

Requires extra `sound`.

__Arguments__

- **wav_file (str/filepath)**: The file that contains the original sound pattern to listen for.
- **device_index (int, optional)**: The index of the microphone device. Run `pnp_record_sound --list` to get the index.
If not specified pyAudio will try to find a capable device.</br>
- **mode (Union[pearson,std], optional)**: Correlation/similarity method. Default is pearson.</br>
- **sensitivity_offset (float, optional)**: Adjusts sensitivity for similarity.
Positive means less sensitive; negative is more sensitive. You should try out 0.1 steps. Default is 0.0.
- **cool_down (duration literal, optional)**: Prevents the pull to emit more than one sound detection event per
cool down duration. Default is 10 seconds.
- **ignore_overflow (bool, optional)**: If set to True any buffer overflows due to slow realtime processing will be ignored.
    Otherwise an exception will be thrown.

Hints:
* You can list your available input devices: `pnp_record_sound --list`
* You can record a wav file from an input device: `pnp_record_sound <out.wav> <seconds_to_record> --index=<idx>`
* This one is _not_ pre-installed when using the docker image. Would be grateful if anyone can integrate it


__Result__

Will only emit the event below when the correlation coefficient is above or equal the threshold.

```yaml
{
    "data": ding,  # Name of the wav_file without path and extension
    "corrcoef": 0.82,  # Correlation coefficient probably between [-1;+1] for pearson
    "threshold": 0.6  # Threshold influenced by sensitivity_offset
}
```

__Examples__

```yaml
- name: sound_detector
  pull:
    plugin: pnp.plugins.pull.sensor.Sound
    args:
      wav_file: doorbell.wav  # The file to compare for similarity
      device_index:  # The index of the microphone devices. If not specified pyAudio will try to find a capable device
      mode: pearson  # Use pearson correlation coefficient [pearson, std]
      sensitivity_offset: 0.1  # Adjust sensitivity. Positive means less sensitive; negative is more sensitive
      cool_down: 3s  # Prevents the pull to emit more than one sound detection event every 3 seconds
      ignore_overflow: true  # Some devices might be too slow to process the stream in realtime. Ignore any buffer overflow errors.
  push:
    - plugin: pnp.plugins.push.simple.Echo

```
