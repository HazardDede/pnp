import logging
from logging import LogRecord

import pytest
from mock import patch, MagicMock

from pnp.logging import SlackHandler, DEFAULT_USERNAME, DEFAULT_EMOJI


@patch('pnp.logging.slacker.Slacker')
def test_logger_emit_for_smoke(slacker_mock):
    slacker_mock.return_value = MagicMock()

    dut = SlackHandler(
        api_key='doesnt_matter',
        channel='pytest',
        fire_and_forget=False
    )
    dut.emit(LogRecord(
        name='pytest',
        level=logging.ERROR,
        pathname='doesnt_matter',
        lineno=42,
        msg='LogRecord from pytest',
        args=None,
        exc_info=None
    ))

    slacker_mock.return_value.chat.post_message.assert_called_once_with(
        text=None,
        channel='#pytest',
        username=DEFAULT_USERNAME,
        icon_url=None,
        icon_emoji=DEFAULT_EMOJI,
        attachments=[{
            'color': 'danger',
            'fields': [{'title': 'LogRecord from pytest', 'short': False}]
        }]
    )


@patch('pnp.logging.slacker.Slacker')
def test_ping_users_existing_user(slacker_mock):
    # user_list = self.slacker.users.list().body['members']
    slacker_mock.return_value = MagicMock()
    slacker_mock.return_value.users.list.return_value.body = {
        'members': [{
            'id': 42,
            'name': 'pytest_user',
            'profile': {
                'real_name': 'PyTest',
                'display_name': 'PyTest'
            }
        }]
    }
    dut = SlackHandler(
        api_key='doesnt_matter',
        channel='pytest',
        ping_users=['pytest_user'],
        fire_and_forget=False
    )
    assert dut.ping_user_ids == [42]

    dut.emit(LogRecord(
        name='pytest',
        level=logging.ERROR,
        pathname='doesnt_matter',
        lineno=42,
        msg='LogRecord from pytest',
        args=None,
        exc_info=None
    ))

    slacker_mock.return_value.chat.post_message.assert_called_once_with(
        text="<@42> ",
        channel='#pytest',
        username=DEFAULT_USERNAME,
        icon_url=None,
        icon_emoji=DEFAULT_EMOJI,
        attachments=[{
            'color': 'danger',
            'fields': [{'title': 'LogRecord from pytest', 'short': False}]
        }]
    )


@patch('pnp.logging.slacker.Slacker')
def test_ping_users_non_existing_user(slacker_mock):
    # user_list = self.slacker.users.list().body['members']
    slacker_mock.return_value = MagicMock()
    slacker_mock.return_value.users.list.return_value.body = {
        'members': [{
            'id': 42,
            'name': 'pytest_user',
            'profile': {
                'real_name': 'PyTest',
                'display_name': 'PyTest'
            }
        }]
    }
    with pytest.raises(RuntimeError) as exc:
        SlackHandler(
            api_key='doesnt_matter',
            channel='pytest',
            ping_users=['doesnotexist'],
            fire_and_forget=False
        )
    assert "User not found in Slack users list: doesnotexist" in str(exc)
