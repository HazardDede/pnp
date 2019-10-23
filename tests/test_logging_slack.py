import logging
import sys
from logging import LogRecord

import pytest
from mock import patch, MagicMock

from pnp.logging import SlackHandler


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
        username=SlackHandler.DEFAULT_USERNAME,
        icon_url=None,
        icon_emoji=SlackHandler.DEFAULT_EMOJI,
        attachments=[{
            'color': 'danger',
            'fields': [{'title': 'LogRecord from pytest', 'short': False}]
        }]
    )


@patch('pnp.logging.slacker.Slacker')
def test_logger_emit_with_trace(slacker_mock):
    slacker_mock.return_value = MagicMock()

    dut = SlackHandler(
        api_key='doesnt_matter',
        channel='pytest',
        fire_and_forget=False
    )
    dut.MAX_ATTACHMENT_CHARS = 1000
    try:
        raise Exception("EXCEPTION RAISED ON PURPOSE!")
    except Exception:
        dut.emit(LogRecord(
            name='pytest',
            level=logging.ERROR,
            pathname='doesnt_matter',
            lineno=42,
            msg='LogRecord from pytest',
            args=None,
            exc_info=sys.exc_info()
        ))

    slacker_mock.return_value.chat.post_message.assert_called_once_with(
        text=None,
        channel='#pytest',
        username=SlackHandler.DEFAULT_USERNAME,
        icon_url=None,
        icon_emoji=SlackHandler.DEFAULT_EMOJI,
        attachments=[{
            'color': 'danger',
            'fields': [{
                'title': 'LogRecord from pytest',
                'short': False,
                'value': '```Traceback (most recent call last):\n\n  File "/Users/dennismuth/private/pnp/tests/test_logging_slack.py", line 54, in test_logger_emit_with_trace\n    raise Exception("EXCEPTION RAISED ON PURPOSE!")\n\nException: EXCEPTION RAISED ON PURPOSE!\n```'
            }]
        }]
    )


@patch('pnp.logging.slacker.Slacker')
def test_logger_emit_with_big_trace(slacker_mock):
    slacker_mock.return_value = MagicMock()

    dut = SlackHandler(
        api_key='doesnt_matter',
        channel='pytest',
        fire_and_forget=False
    )
    dut.MAX_ATTACHMENT_CHARS = 26
    try:
        raise Exception("EXCEPTION RAISED ON PURPOSE!")
    except Exception:
        dut.emit(LogRecord(
            name='pytest',
            level=logging.ERROR,
            pathname='doesnt_matter',
            lineno=42,
            msg='LogRecord from pytest',
            args=None,
            exc_info=sys.exc_info()
        ))

    slacker_mock.return_value.chat.post_message.assert_called_once_with(
        text=None,
        channel='#pytest',
        username=SlackHandler.DEFAULT_USERNAME,
        icon_url=None,
        icon_emoji=SlackHandler.DEFAULT_EMOJI,
        attachments=[{
            'color': 'danger',
            'fields': [{
                'title': 'LogRecord from pytest',
                'short': False,
                'value': '``` RAISED ON PURPOSE!\n```'
            }]
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
        username=SlackHandler.DEFAULT_USERNAME,
        icon_url=None,
        icon_emoji=SlackHandler.DEFAULT_EMOJI,
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
