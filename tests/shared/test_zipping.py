import os
import tempfile
from zipfile import ZipFile

from pnp.shared.zipping import zipignore, zipdir, zipfiles


def test_zipignore_parser():
    path = os.path.join(os.path.dirname(__file__), '../resources/zipping')
    assert list(zipignore(path, file_name='zipignore')) == [
        '.git',
        '__pycache__',
        '*.pyc',
        'zipignore'
    ]


def test_zipdir_no_ignore():
    path = os.path.join(os.path.dirname(__file__), '../resources/zipping/testdir')
    with tempfile.TemporaryDirectory() as tmpdir:
        out_zip = os.path.join(tmpdir, 'all.zip')
        zipdir(path, out_zip)
        assert set(ZipFile(out_zip).namelist()) == {'1', '2/2', '2/3/3', '2/3/4', '.zipignore'}


def test_zipdir_with_ignore():
    path = os.path.join(os.path.dirname(__file__), '../resources/zipping/testdir')
    ignore_list = zipignore(path)
    with tempfile.TemporaryDirectory() as tmpdir:
        out_zip = os.path.join(tmpdir, 'all.zip')
        zipdir(path, out_zip, ignore_list)
        assert set(ZipFile(out_zip).namelist()) == {'1', '2/2'}


def test_zipfiles():
    file1 = os.path.join(os.path.dirname(__file__), '../resources/zipping/testdir/1')
    file2 = os.path.join(os.path.dirname(__file__), '../resources/zipping/testdir/2/2')

    with tempfile.TemporaryDirectory() as tmpdir:
        out_zip = os.path.join(tmpdir, 'files.zip')
        zipfiles([file1, file2], out_zip)

        assert set(ZipFile(out_zip).namelist()) == {'1', '2'}
