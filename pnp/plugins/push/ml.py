"""Machine learning related push plugins."""

import io
import os

from pnp import validator
from pnp.plugins import load_optional_module
from pnp.plugins.push import PushBase, enveloped, drop_envelope
from pnp.utils import make_list, auto_str_ignore
from pnp.validator import one_not_none


@auto_str_ignore(['known_encodings'])
class FaceR(PushBase):
    """
    FaceR (short one for face recognition) tags known faces in images.
    Output is the image with all faces tagged whether with the known name or an `unknown_label`.
    Default for unknown ones is 'Unknown'.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/ml.FaceR/index.md
    """
    EXTRA = 'faceR'

    def __init__(self, known_faces=None, known_faces_dir=None, unknown_label="Unknown", lazy=False,
                 **kwargs):
        # known_faces -> mapping name -> list of files
        # known_faces_dir -> directory with known faces (filename -> name)
        # unknown_label -> Label for unknown faces
        super().__init__(**kwargs)

        one_not_none(known_faces=known_faces, known_faces_dir=known_faces_dir)
        self.known_faces = known_faces
        validator.is_instance(dict, allow_none=True, known_faces=self.known_faces)
        self.known_faces_dir = known_faces_dir and str(known_faces_dir)
        if self.known_faces_dir:
            validator.is_directory(known_faces_dir=self.known_faces_dir)

        if not lazy:
            self._configure()
        else:
            self.known_names = None
            self.known_encodings = None
            self.face_recognition = None

        self.unknown_label = str(unknown_label)

    def _load_fencodings(self, fp):
        img = self.face_recognition.load_image_file(fp)
        return self.face_recognition.face_encodings(img)[0]

    def _load_from_mapping(self, mapping):
        def _loop():
            for name, fps in mapping.items():
                for fp in make_list(fps):
                    yield name, self._load_fencodings(fp)
        targets = list(_loop())
        return [name for name, _ in targets], [fp for _, fp in targets]

    def _load_from_directory(self, directory):
        def _loop():
            accepted = ('.tif', '.tiff', '.gif', '.jpeg', '.jpg', '.jif', '.jfif', '.png')
            for file in os.listdir(os.fsencode(directory)):
                filename = os.fsdecode(file)
                if filename.lower().endswith(accepted):
                    # strip the extension from the filename
                    yield (
                        os.path.splitext(filename)[0],
                        self._load_fencodings(os.path.join(directory, filename))
                    )
        targets = list(_loop())
        return [name for name, _ in targets], [fp for _, fp in targets]

    def _configure(self):
        # Do not break the complete module, when extra_packages are not present
        self.face_recognition = load_optional_module('face_recognition', self.EXTRA)

        # If both are set known_faces is the default
        if self.known_faces:
            self.known_names, self.known_encodings = self._load_from_mapping(self.known_faces)
        else:
            self.known_names, self.known_encodings = self._load_from_directory(self.known_faces_dir)

    @staticmethod
    def _tag_image(unknown_image, tags):
        from PIL import Image, ImageDraw  # pylint: disable=import-error

        # Convert the image to a PIL-format image so that we can draw on top of it with the
        # Pillow library. See http://pillow.readthedocs.io/ for more about PIL/Pillow
        pil_image = Image.fromarray(unknown_image)
        # Create a Pillow ImageDraw Draw instance to draw with
        draw = ImageDraw.Draw(pil_image)
        try:
            for name, (top, right, bottom, left) in tags:
                # Draw a box around the face using the Pillow module
                draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

                # Draw a label with a name below the face
                _, text_height = draw.textsize(name)
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

    @enveloped
    @drop_envelope
    def push(self, payload):
        if not self.face_recognition:
            self._configure()

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
                known_faces=list({name for name, _ in tags if name != self.unknown_label})
            )
        finally:
            del out_io
