import os

from ..conftest import path_to_faces

try:
    import face_recognition
    skip = False
except ImportError:
    skip = True
    print("Skipping faceR tests due to missing package")

if not skip:
    def test_facer_with_directory():
        from pnp.plugins.push.ml import FaceR
        dut = FaceR(name='pytest', known_faces_dir=path_to_faces())

        assert len(dut.known_encodings) == 2
        assert len(dut.known_names) == 2
        assert set(dut.known_names) == {'obama', 'trump'}


    def test_facer_with_mapping():
        from pnp.plugins.push.ml import FaceR
        faces_dir = path_to_faces()
        mapping = {'trump': os.path.join(faces_dir, 'trump.jpg'), 'obama': os.path.join(faces_dir, 'obama.jpg')}
        dut = FaceR(name='pytest', known_faces=mapping)

        assert len(dut.known_encodings) == 2
        assert len(dut.known_names) == 2
        assert set(dut.known_names) == {'obama', 'trump'}


    def test_facer_find_known():
        from pnp.plugins.push.ml import FaceR
        dut = FaceR(name='pytest', known_faces_dir=path_to_faces())

        trump_jpg = os.path.join(path_to_faces(), 'trump.jpg')
        with open(trump_jpg, 'rb') as fs:
            jpg = fs.read()
        res = dut.push(jpg)

        assert isinstance(res, dict)
        assert all(item in res for item in ['tagged_image', 'no_of_faces', 'known_faces'])
        assert res['no_of_faces'] == 1
        assert 'trump' in res['known_faces']