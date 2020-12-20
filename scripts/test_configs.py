import os

import pytest
from argresolver.utils import modified_environ
from ruamel import yaml

from pnp.app import Application

DOCS_PATH = os.path.join(os.path.dirname(__file__), '../docs')
FITBIT_AUTH_PATH = '/tmp/fitbit.conf'
GMAIL_AUTH_PATH = '/tmp/gmail.conf'
MOTIONEYE_MEDIA_PATH = '/tmp/motioneye'
WATCHDIR_PATH = '/tmp/watchdir'
FTPDIR_PATH = '/tmp/ftp'


ENV = {
    'BACKUP_DIR': '/tmp',
    'DROPBOX_API_KEY': 'blub',
    'FITBIT_AUTH': FITBIT_AUTH_PATH,
    'FTP_DIR': FTPDIR_PATH,
    'GMAIL_TOKEN_FILE': GMAIL_AUTH_PATH,
    'GMAIL_RECIPIENT': 'somebody@somehost.net',
    'HA_TOKEN': 'abcdefg',
    'HA_URL': 'http://localhost:8123',
    'MESSAGE': 'Hello World',
    'MQTT_HOST': 'localhost',
    'MQTT_BASE_TOPIC': 'anytopic',
    'OPENWEATHER_API_KEY': 'baz',
    'SLACK_API_KEY': 'the_slack_token',
    'WATCH_DIR': WATCHDIR_PATH,
    'ZWAY_USER': 'foo',
    'ZWAY_PASSWORD': 'bar',
}


def get_files_from_path(base_path, extensions):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(extensions):
                yield os.path.join(root, file)


def get_files():
    extensions = ('.yaml', '.yml', '.json')
    return get_files_from_path(DOCS_PATH, extensions)


@pytest.yield_fixture(scope='module', autouse=True)
def setup():
    os.makedirs("/tmp/camera", exist_ok=True)
    os.makedirs("/tmp/faces", exist_ok=True)
    os.makedirs("/tmp/counter", exist_ok=True)
    os.makedirs(MOTIONEYE_MEDIA_PATH, exist_ok=True)
    os.makedirs(WATCHDIR_PATH, exist_ok=True)
    os.makedirs(FTPDIR_PATH, exist_ok=True)
    fitbit_auth = dict(access_token='<access_token>', refresh_token='refresh_token',
                       client_id='<client_id>', client_secret='<client_secret>',
                       expires_at=12345678)
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
    import sys
    sys.exit(pytest.main([os.path.dirname(__file__), '-v']))
