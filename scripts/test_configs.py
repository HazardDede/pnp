import os
from itertools import chain

import pytest
from argresolver.utils import modified_environ

from pnp.app import Application

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config')
DOCS_PATH = os.path.join(os.path.dirname(__file__), '../docs')

ENV = {
    'ZWAY_USER': 'foo',
    'ZWAY_PASSWORD': 'bar',
    'OPENWEATHER_API_KEY': 'baz'
}


def get_files_from_path(base_path, extensions):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(extensions):
                yield os.path.join(root, file)


def get_files():
    extensions = ('.yaml', '.yml', '.json')
    return chain(get_files_from_path(CONFIG_PATH, extensions), get_files_from_path(DOCS_PATH, extensions))


@pytest.yield_fixture(scope='module', autouse=True)
def setup():
    os.makedirs("/tmp/camera", exist_ok=True)
    os.makedirs("/tmp/faces", exist_ok=True)
    os.makedirs("/tmp/counter", exist_ok=True)


@pytest.mark.parametrize("config_file", get_files())
def test_bundled_config(config_file):
    with modified_environ(**ENV):
        app = Application.from_file(config_file)
        assert app is not None


if __name__ == '__main__':
    pytest.main([os.path.dirname(__file__), '-v'])
