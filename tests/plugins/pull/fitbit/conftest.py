import os
import tempfile

import pytest
import yaml


@pytest.yield_fixture(scope='function')
def token_file():
    tokens = {
        'client_id': '123456',
        'client_secret': 'abcdefg',
        'access_token': 'zyx',
        'refresh_token': 'refresh_token',
        'expires_at': 123.567
    }
    with tempfile.NamedTemporaryFile('w') as tf:
        yaml.dump(tokens, tf)
        tf.flush()
        os.fsync(tf)
        yield tf.name
