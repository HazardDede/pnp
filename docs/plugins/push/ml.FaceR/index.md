# pnp.plugins.push.ml.FaceR

FaceR (short one for face recognition) tags known faces in images. Output is the image with all faces tagged whether
with the known name or an `unknown_label`. Default for unknown ones is 'Unknown'.

Known faces can be ingested either by a directory of known faces (`known_faces_dir`) or by mapping of `known_faces`
(dictionary: name -> [list of face files]).

The `payload` passed to the `push` method is expected to be a valid byte array that represents an image in memory.

Hint: This one is _not_ pre-installed when using the docker image. Would be grateful if anyone can integrate it

__Arguments__

- **known_faces (dict<str, file_path as str>, optional)**: Mapping of a person's name to a list of images that contain
    the person's face. Default is None.
- **known_faces_dir (str, optional)**: A directory containing images with known persons (file_name -> person's name).
    Default is None.
- **unknown_label (str, optional)**: Tag label of unknown faces. Default is 'Unknown'.
- **lazy (bool, optional)**: If set to True the face encodings will be loaded when the first push is executed (lazy);
    otherwise the encodings are loaded when the plugin is initialized (during `__init__`).

You have to specify either `known_faces` or `known_faces_dir`. If both are unsupplied the push will fail.

__Result__

Will return a dictionary that contains the bytes of the tagged image (key `tagged_image`) and metadata (`no_of_faces`,
`known_faces`)

```yaml
{
    'tagged_image': <bytes of tagged image>
    'no_of_faces': 2
    'known_faces': ['obama']
}
```

__Examples__

```yaml
- name: faceR
  pull:
    plugin: pnp.plugins.pull.fs.FileSystemWatcher
    args:
      path: "/tmp/camera"
      recursive: true
      patterns: "*.jpg"
      ignore_directories: true
      case_sensitive: false
      events: [created]
      load_file: true
      mode: binary
      base64: false
  push:
    plugin: pnp.plugins.push.ml.FaceR
    args:
      known_faces_dir: "/tmp/faces"
      unknown_label: "don't know him"
      lazy: true

```
