import os
import tempfile
from zipfile import ZipFile

import pytest

from pnp.plugins.push.fs import Zipper


@pytest.mark.asyncio
async def test_zipper_push_init_directory():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', source=path, out_path=tmpdir)
        zip_file_name = await dut.push('any')
        assert zip_file_name == os.path.join(tmpdir, 'testdir' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1', '2/2'}


@pytest.mark.asyncio
async def test_zipper_push_payload_directory():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', out_path=tmpdir)
        zip_file_name = await dut.push(path)
        assert zip_file_name == os.path.join(tmpdir, 'testdir' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1', '2/2'}


@pytest.mark.asyncio
async def test_zipper_push_init_file():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir/1')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', source=path, out_path=tmpdir)
        zip_file_name = await dut.push('any')
        assert zip_file_name == os.path.join(tmpdir, '1' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1'}


@pytest.mark.asyncio
async def test_zipper_push_payload_file():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir/1')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', out_path=tmpdir)
        zip_file_name = await dut.push(path)
        assert zip_file_name == os.path.join(tmpdir, '1' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1'}


@pytest.mark.asyncio
async def test_zipper_push_archive_name():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', out_path=tmpdir, archive_name='foo.zip')
        zip_file_name = await dut.push(path)
        assert zip_file_name == os.path.join(tmpdir, 'foo' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1', '2/2'}


@pytest.mark.asyncio
async def test_zipper_push_archive_name_override():
    path = os.path.join(os.path.dirname(__file__), '../../resources/zipping/testdir')
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = Zipper(name='pytest', out_path=tmpdir)
        zip_file_name = await dut.push({'data': path, 'archive_name': 'foo.zip'})
        assert zip_file_name == os.path.join(tmpdir, 'foo' + '.zip')
        assert set(ZipFile(zip_file_name).namelist()) == {'1', '2/2'}
