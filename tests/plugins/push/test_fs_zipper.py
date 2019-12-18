import os
import tempfile
from zipfile import ZipFile

from pnp.plugins.push.fs import Zipper


def test_zipper_push_init_directory():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', source=path, out_path=tmpdir)
        zip_file_name = dut.push('any')
        assert zip_file_name == os.path.join(tmpdir, 'testdir' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1', '2/2'}


def test_zipper_push_payload_directory():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', out_path=tmpdir)
        zip_file_name = dut.push(path)
        assert zip_file_name == os.path.join(tmpdir, 'testdir' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1', '2/2'}


def test_zipper_push_init_file():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir/1')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', source=path, out_path=tmpdir)
        zip_file_name = dut.push('any')
        assert zip_file_name == os.path.join(tmpdir, '1' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1'}


def test_zipper_push_payload_file():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir/1')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', out_path=tmpdir)
        zip_file_name = dut.push(path)
        assert zip_file_name == os.path.join(tmpdir, '1' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1'}
