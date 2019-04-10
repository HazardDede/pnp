import os

import pytest
from pytest import yield_fixture

from pnp.plugins.pull.fs import Size
from tests.conftest import resource_path


@yield_fixture
def directory():
    yield resource_path('faces')


def test_fs_size_non_mapping(directory):
    dut = Size(paths=[
        directory, os.path.join(directory, 'obama.jpg'), os.path.join(directory, 'trump.jpg')
    ], name='pytest')

    res = dut.poll()

    assert res == {
        'faces': res.get('obama.jpg') + res.get('trump.jpg'),
        'obama.jpg': 45136,
        'trump.jpg': 13056
    }


def test_fs_size_mapping(directory):
    dut = Size(paths={
        'root': directory,
        'obama': os.path.join(directory, 'obama.jpg'),
        'trump': os.path.join(directory, 'trump.jpg')
    }, name='pytest')

    res = dut.poll()

    assert res == {
        'root': res.get('obama') + res.get('trump'),
        'obama': 45136,
        'trump': 13056
    }


def test_fs_size_non_existent(directory):
    with pytest.raises(FileNotFoundError):
        Size(paths={
            'root': '/this/one/does/not/exist!'
        }, name='pytest').poll()

    res = Size(paths={
        'root': '/this/one/does/not/exist!'
    }, name='pytest', fail_on_error=False).poll()

    assert res == {'root': None}
