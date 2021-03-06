import pytest
from mock import MagicMock

from pnp.plugins.push.notify import Slack


@pytest.mark.asyncio
async def test_slack_push(mocker):
    slacker_mock = mocker.patch('pnp.plugins.push.notify.slacker.Slacker')
    slacker_mock.return_value = MagicMock()

    dut = Slack(
        api_key='doesnt_matter',
        channel='pytest',
        name='pytest'
    )
    await dut.push('Simple message')

    slacker_mock.return_value.chat.post_message.assert_called_once_with(
        text='Simple message',
        channel='#pytest',
        username=Slack.DEFAULT_USERNAME,
        icon_emoji=Slack.DEFAULT_EMOJI
    )


@pytest.mark.asyncio
async def test_slack_push_with_ping_user(mocker):
    slacker_mock = mocker.patch('pnp.plugins.push.notify.slacker.Slacker')
    slacker_mock.return_value = MagicMock()
    slacker_mock.return_value.users.list.return_value.body = {
        'members': [{
            'id': 42,
            'name': 'pytest_user',
            'profile': {
                'real_name': 'PyTest',
                'display_name': 'PyTest'
            }
        }, {
            'id': 99,
            'name': 'another_user',
            'profile': {
                'real_name': 'anon',
                'display_name': 'anusr'
            }
        }]
    }

    dut = Slack(
        api_key='doesnt_matter',
        channel='pytest',
        ping_users=['PyTest'],
        name='pytest'
    )

    # Use the real_name
    await dut.push('Simple message')
    slacker_mock.return_value.chat.post_message.assert_called_with(
        text='<@42> Simple message',
        channel='#pytest',
        username=Slack.DEFAULT_USERNAME,
        icon_emoji=Slack.DEFAULT_EMOJI
    )

    # Envelope override with name
    await dut.push({'data': 'Simple message', 'ping_users': 'another_user'})
    slacker_mock.return_value.chat.post_message.assert_called_with(
        text='<@99> Simple message',
        channel='#pytest',
        username=Slack.DEFAULT_USERNAME,
        icon_emoji=Slack.DEFAULT_EMOJI
    )

    # Envelope override with unknown user
    await dut.push({'data': 'Simple message', 'ping_users': 'unknown_user'})
    slacker_mock.return_value.chat.post_message.assert_called_with(
        text='Simple message',
        channel='#pytest',
        username=Slack.DEFAULT_USERNAME,
        icon_emoji=Slack.DEFAULT_EMOJI
    )
