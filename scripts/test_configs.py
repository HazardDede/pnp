import os
from itertools import chain
from ruamel import yaml

import pytest
from argresolver.utils import modified_environ

from pnp.app import Application

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config')
DOCS_PATH = os.path.join(os.path.dirname(__file__), '../docs')
FITBIT_AUTH_PATH = '/tmp/fitbit.conf'
GMAIL_AUTH_PATH = '/tmp/gmail.conf'
MOTIONEYE_MEDIA_PATH = '/tmp/motioneye'

ENV = {
    'ZWAY_USER': 'foo',
    'ZWAY_PASSWORD': 'bar',
    'OPENWEATHER_API_KEY': 'baz',
    'MESSAGE': 'Hello World',
    'DROPBOX_API_KEY': 'blub',
    'PUSHBULLET_API_KEY': 'bla',
    'FITBIT_AUTH': FITBIT_AUTH_PATH,
    'HA_TOKEN': 'abcdefg',
    'HA_URL': 'http://localhost:8123',
    'MQTT_HOST': 'localhost',
    'GMAIL_TOKEN_FILE': GMAIL_AUTH_PATH,
    'GMAIL_RECIPIENT': 'somebody@somehost.net',
    'MOTIONEYE_MEDIA_PATH': MOTIONEYE_MEDIA_PATH
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
    os.makedirs(MOTIONEYE_MEDIA_PATH, exist_ok=True)
    fitbit_auth = dict(access_token='<access_token>', refresh_token='refresh_token', client_id='<client_id>',
                       client_secret='<client_secret>', expires_at=12345678)
    with open(FITBIT_AUTH_PATH, 'w') as fp:
        yaml.dump(fitbit_auth, fp)
    with open(GMAIL_AUTH_PATH, 'w') as fp:
        fp.write("")


@pytest.mark.parametrize("config_file", get_files())
def test_bundled_config(config_file):
    with modified_environ(**ENV):
        app = Application.from_file(config_file)
        assert app is not None


if __name__ == '__main__':
    pytest.main([os.path.dirname(__file__), '-v'])
