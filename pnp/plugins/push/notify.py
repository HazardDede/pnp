"""Notification related push plugins."""

from typing import Any, Dict, List, Optional

import slacker

from pnp.plugins.push import SyncPush, enveloped, parse_envelope
from pnp.typing import Envelope, Payload
from pnp.utils import make_list


class Slack(SyncPush):
    """
    Sends a message to slack. Optionally you can specify users to ping.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#notify-slack
    """
    __REPR_FIELDS__ = ['channel', 'emoji', 'ping_users', 'username']

    DEFAULT_USERNAME = 'PnP'
    DEFAULT_EMOJI = ':robot:'

    def __init__(self, api_key: str, channel: str, username: str = DEFAULT_USERNAME,
                 emoji: str = DEFAULT_EMOJI, ping_users: Optional[List[str]] = None,
                 **kwargs: Any):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.channel = self._parse_channel(channel)
        self.username = self._parse_username(username)
        self.emoji = self._parse_emoji(emoji)
        self.ping_users = self._parse_ping_users(ping_users)
        self._user_cache = dict()  # type: Dict[str, str]
        self._slacker = slacker.Slacker(api_key)

    @staticmethod
    def _parse_channel(val: Any):
        channel = str(val)
        if not channel.startswith('#'):
            channel = '#' + channel
        return channel

    @staticmethod
    def _parse_ping_users(val: Any):
        return make_list(val or [])

    @staticmethod
    def _parse_username(val: Any):
        return str(val)

    @staticmethod
    def _parse_emoji(val: Any):
        return str(val)

    def _refresh_user_cache(self) -> Dict[str, int]:
        def _helper() -> Any:
            for usr in user_list:
                yield {usr['name']: usr['id']}
                yield {usr['profile']['real_name']: usr['id']}
                yield {usr['profile']['display_name']: usr['id']}

        self.logger.debug("User cache invalidation")
        user_list = self._slacker.users.list().body['members']
        self._user_cache = {k: v for d in _helper() for k, v in d.items()}

    def _lookup_users(self, ping_users: List[str]):
        if not ping_users:
            return

        refreshed = False
        if not self._user_cache:
            self._refresh_user_cache()
            refreshed = True

        for user in ping_users:
            user_id = self._user_cache.get(user, None)
            if user_id is None and not refreshed:
                # Maybe our cache is too old and some users were added in the meantime
                self._refresh_user_cache()
                refreshed = True
                user_id = self._user_cache.get(user, None)

            if user_id is None:  # Still not there...
                self.logger.warning("User not found in Slack users list: %s", user)
            else:
                yield user_id

    def _build_message_text(self, text: str, ping_users: List[str]):
        ping_user_ids = self._lookup_users(ping_users)

        for user_id in ping_user_ids:
            text = "<@{user}> {text}".format(user=user_id, text=text)

        return text

    @enveloped
    @parse_envelope('channel')
    @parse_envelope('username')
    @parse_envelope('emoji')
    @parse_envelope('ping_users')
    def _push(self, channel: str, username: str, emoji: str,  # pylint: disable=arguments-differ
              ping_users: List[str], envelope: Envelope, payload: Payload):

        text = self._build_message_text(str(payload), ping_users)
        self._slacker.chat.post_message(
            text=text,
            channel=channel,
            username=username,
            icon_emoji=emoji
        )

        return {'data': payload, **envelope} if envelope else payload
