import os

import pytest


def path_to_faces():
    return os.path.join(os.path.dirname(__file__), '../../resources/faces')


def _package_installed():
    try:
        import face_recognition
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _package_installed(), reason="requires package face-recognition")
def test_facer_with_directory():
    from pnp.plugins.push.ml import FaceR
    dut = FaceR(name='pytest', known_faces_dir=path_to_faces())

    assert len(dut.known_encodings) == 2
    assert len(dut.known_names) == 2
    assert set(dut.known_names) == {'obama', 'trump'}


@pytest.mark.skipif(not _package_installed(), reason="requires package face-recognition")
def test_facer_with_mapping():
    from pnp.plugins.push.ml import FaceR
    faces_dir = path_to_faces()
    mapping = {'trump': os.path.join(faces_dir, 'trump.jpg'), 'obama': os.path.join(faces_dir, 'obama.jpg')}
    dut = FaceR(name='pytest', known_faces=mapping)

    assert len(dut.known_encodings) == 2
    assert len(dut.known_names) == 2
    assert set(dut.known_names) == {'obama', 'trump'}


@pytest.mark.asyncio
@pytest.mark.skipif(not _package_installed(), reason="requires package face-recognition")
async def test_facer_find_known():
    from pnp.plugins.push.ml import FaceR
    dut = FaceR(name='pytest', known_faces_dir=path_to_faces())

    trump_jpg = os.path.join(path_to_faces(), 'trump.jpg')
    with open(trump_jpg, 'rb') as fs:
        jpg = fs.read()
    res = await dut.push(jpg)

    assert isinstance(res, dict)
    assert all(item in res for item in ['tagged_image', 'no_of_faces', 'known_faces'])
    assert res['no_of_faces'] == 1
    assert 'trump' in res['known_faces']


@pytest.mark.asyncio
@pytest.mark.skipif(not _package_installed(), reason="requires package face-recognition")
async def test_facer_find_known_lazy_mode():
    from pnp.plugins.push.ml import FaceR
    dut = FaceR(name='pytest', known_faces_dir=path_to_faces(), lazy=True)
    assert dut.face_recognition is None
    assert dut.known_names is None
    assert dut.known_encodings is None

    trump_jpg = os.path.join(path_to_faces(), 'trump.jpg')
    with open(trump_jpg, 'rb') as fs:
        jpg = fs.read()
    await dut.push(jpg)

    assert dut.face_recognition is not None
    assert dut.known_names is not None
    assert dut.known_encodings is not None
