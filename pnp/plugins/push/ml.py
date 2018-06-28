import io
import os

from . import PushBase
from ...utils import make_list, auto_str_ignore
from ...validator import Validator


@auto_str_ignore(['known_encodings'])
class FaceR(PushBase):
    """
    FaceR (short one for face recognition) tags known faces in images. Output is the image with the
    all faces tagged whether with the known name or an `unknown_label`. Default for unknown ones is 'Unknown'.

    Known faces can be ingested either by a directory of known faces (`known_faces_dir`) or by mapping of `known_faces`
    (dictionary: name -> [list of face files]).

    The `payload` passed to the `push` method is expected to be a valid byte array that represents an image in memory.

    Args:
        known_faces (dict): Mapping of a person's name to a list of images that contain the person's face.
        known_faces_dir (str): A directory containing images with knonwn persons (file_name -> person's name)
        unknown_label (str): Tag label of unknown faces.

    Returns:
        If the push is performed the resulting dictionary looks like
        {
            'tagged_image': <bytes of tagged image>
            'no_of_faces': 2
            'known_faces': ['obama']
        }

    Example configuration:

        name: faceR
        pull:
          plugin: pnp.plugins.pull.fs.FileSystemWatcher
          args:
            path: "/tmp"
            recursive: True
            patterns: "*.jpg"
            ignore_directories: True
            case_sensitive: False
            events: [created]
            load_file: True
            mode: binary
            base64: False
        push:
          plugin: pnp.plugins.push.ml.FaceR
          args:
            known_faces_dir: /path/to/known/faces
            unknown_label: "don't know him"
    """
    def __init__(self, known_faces=None, known_faces_dir=None, unknown_label="Unknown", **kwargs):
        # known_faces -> mapping name -> list of files
        # known_faces_dir -> directory with known faces (filename -> name)
        # unknown_label -> Label for unknown faces
        super().__init__(**kwargs)

        # Do not break the complete module, when extra_packages are not present
        self.face_recognition = __import__("face_recognition")

        Validator.one_not_none(known_faces=known_faces, known_faces_dir=known_faces_dir)
        # If both are set known_faces is the default
        if known_faces is not None:
            # Process known faces mapping
            self.known_names, self.known_encodings = self._load_from_mapping(known_faces)
        else:
            # Process known faces directory
            Validator.is_directory(known_faces_dir=known_faces_dir)
            self.known_names, self.known_encodings = self._load_from_directory(known_faces_dir)

        self.unknown_label = str(unknown_label)

    def _load_from_mapping(self, m):
        def _loop():
            for name, fps in m.items():
                for fp in make_list(fps):
                    yield name, self._load_fencodings(fp)
        t = list(_loop())
        return [name for name, _ in t], [fp for _, fp in t]

    def _load_from_directory(self, directory):
        def _loop():
            accepted = ('.tif', '.tiff', '.gif', '.jpeg', '.jpg', '.jif', '.jfif', '.png')
            for file in os.listdir(os.fsencode(directory)):
                filename = os.fsdecode(file)
                if filename.endswith(accepted):
                    # strip the extension from the filename
                    yield os.path.splitext(filename)[0], self._load_fencodings(os.path.join(directory, filename))
        t = list(_loop())
        return [name for name, _ in t], [fp for _, fp in t]

    def _load_fencodings(self, fp):
        img = self.face_recognition.load_image_file(fp)
        return self.face_recognition.face_encodings(img)[0]

    def _tag_image(self, unknown_image, tags):
        from PIL import Image, ImageDraw

        # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
        # See http://pillow.readthedocs.io/ for more about PIL/Pillow
        pil_image = Image.fromarray(unknown_image)
        # Create a Pillow ImageDraw Draw instance to draw with
        draw = ImageDraw.Draw(pil_image)
        try:
            for name, (top, right, bottom, left) in tags:
                # Draw a box around the face using the Pillow module
                draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

                # Draw a label with a name below the face
                text_width, text_height = draw.textsize(name)
                draw.rectangle(
                    ((left, bottom - text_height - 10), (right, bottom)),
                    fill=(0, 0, 255),
                    outline=(0, 0, 255)
                )
                draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

            return pil_image
        finally:
            # Remove the drawing library from memory as per the Pillow docs
            del draw

    def push(self, payload):
        envelope, payload = self.envelope_payload(payload)
        # Load unknown image and find faces
        unknown_image = self.face_recognition.load_image_file(io.BytesIO(payload))
        face_locations = self.face_recognition.face_locations(unknown_image)
        face_encodings = self.face_recognition.face_encodings(unknown_image, face_locations)

        tags = []
        # Loop through each face found in the unknown image
        for flocation, face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = self.face_recognition.compare_faces(self.known_encodings, face_encoding)
            name = self.unknown_label
            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_names[first_match_index]
            tags.append((name, flocation))

        # Tag the face locations
        tagged_image = self._tag_image(unknown_image, tags)

        # Save the image to a bytestream
        out_io = io.BytesIO()
        try:
            tagged_image.save(out_io, format='PNG')
            return dict(
                tagged_image=out_io.getvalue(),
                no_of_faces=len(face_locations),
                known_faces=list(set([name for name, _ in tags if name != self.unknown_label]))
            )
        finally:
            del out_io
