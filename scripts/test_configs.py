import os
from itertools import chain

import pytest
from argresolver.utils import modified_environ

from pnp.app import Application

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config')

ENV = {
    'ZWAY_USER': 'foo',
    'ZWAY_PASSWORD': 'bar'
}


def get_files(extension):
    for root, dirs, files in os.walk(CONFIG_PATH):
        for file in files:
            if file.endswith("." + extension):
                yield os.path.join(root, file)


@pytest.yield_fixture(scope='module', autouse=True)
def setup():
    os.makedirs("/tmp/camera", exist_ok=True)
    os.makedirs("/tmp/faces", exist_ok=True)
    os.makedirs("/tmp/counter", exist_ok=True)


@pytest.mark.parametrize("config_file", chain(get_files('yaml'), get_files('json'), get_files('yml')))
def test_bundled_config(config_file):
    with modified_environ(**ENV):
        app = Application.from_file(config_file)
        assert app is not None


if __name__ == '__main__':
    pytest.main([os.path.dirname(__file__), '-v'])
