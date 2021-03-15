import yaml

from pnp.plugins.pull.fitbit import Devices


def test_save_tokens(token_file, mocker):
    fb_mock = mocker.patch('fitbit.Fitbit')
    dut = Devices(config=token_file, name='pytest', instant_run=True)
    dut._load_tokens()
    assert dut._tokens == {
        'client_id': '123456',
        'client_secret': 'abcdefg',
        'access_token': 'zyx',
        'refresh_token': 'refresh_token',
        'expires_at': 123.567
    }
    dut._save_tokens({'access_token': 'access_token', 'refresh_token': 'refresh_token', 'expires_at': 9999.9})
    assert dut._tokens == {
        'client_id': '123456',
        'client_secret': 'abcdefg',
        'access_token': 'access_token',
        'refresh_token': 'refresh_token',
        'expires_at': 9999.9
    }
    with open(token_file, 'r') as tf:
        assert yaml.safe_load(tf) == {
            'client_id': '123456',
            'client_secret': 'abcdefg',
            'access_token': 'access_token',
            'refresh_token': 'refresh_token',
            'expires_at': 9999.9
        }

