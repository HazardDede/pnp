from tempfile import NamedTemporaryFile

import pytest
from box import Box

from pnp.plugins.push.storage import Dropbox


def setup_mock(mock_dbx):
    mock_dbx.return_value.files_upload.return_value.name = "name_42"
    mock_dbx.return_value.files_upload.return_value.id = "id_42"
    mock_dbx.return_value.files_upload.return_value.content_hash = "hash_42"
    mock_dbx.return_value.files_upload.return_value.size = 42
    mock_dbx.return_value.files_upload.return_value.path_display = "path/42"
    mock_dbx.return_value.sharing_create_shared_link.return_value.url = "http://42:42/42?dl=1"
    return mock_dbx


@pytest.mark.asyncio
async def test_dropbox_push_with_file(mocker):
    dbx_mock = setup_mock(mocker.patch('dropbox.Dropbox'))
    dut = Dropbox(name='pytest', api_key='secret', create_shared_link=False)
    with NamedTemporaryFile() as tmp:
        res = await dut.push({'target_file_name': 'tmp', 'data': tmp.name})

    assert isinstance(res, dict)
    res = Box(res)
    assert res.name == "name_42"
    assert res.id == "id_42"
    assert res.content_hash == "hash_42"
    assert res.size == 42
    assert res.path == "path/42"
    assert res.shared_link is None
    assert res.raw_link is None

    dbx_mock.assert_called_with('secret', timeout=None)
    dbx_mock.return_value.files_upload.assert_called()


@pytest.mark.asyncio
async def test_dropbox_push_with_file_and_shared_link(mocker):
    dbx_mock = setup_mock(mocker.patch('dropbox.Dropbox'))
    dut = Dropbox(name='pytest', api_key='secret', target_file_name="42", create_shared_link=True)
    with NamedTemporaryFile() as tmp:
        res = await dut.push(tmp.name)

    assert isinstance(res, dict)
    res = Box(res)
    assert res.shared_link == 'http://42:42/42?dl=1'
    assert res.raw_link == 'http://42:42/42?raw=1'

    dbx_mock.assert_called_with('secret', timeout=None)
    dbx_mock.return_value.files_upload.assert_called()
    dbx_mock.return_value.sharing_create_shared_link.assert_called_with('/42')
