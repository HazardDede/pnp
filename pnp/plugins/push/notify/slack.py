"""Push: notify.Slack."""

from typing import Any, Dict, List, Optional, Iterator

import slacker

from pnp.plugins.push import SyncPush
from pnp.plugins.push.envelope import Envelope
from pnp.typing import Envelope as EnvelopeType, Payload
from pnp.utils import make_list


CONST_USERNAME_DEFAULT = "PnP"
CONST_EMOJI_DEFAULT = ":robot:"


class Slack(SyncPush):
    """
    Sends a message to slack. Optionally you can specify users to ping.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#notify-slack
    """
    __REPR_FIELDS__ = ['channel', 'emoji', 'ping_users', 'username']

    def __init__(
            self, api_key: str, channel: str, username: str = CONST_USERNAME_DEFAULT,
            emoji: str = CONST_EMOJI_DEFAULT, ping_users: Optional[List[str]] = None,
            **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.channel = self._parse_channel(channel)
        self.username = self._parse_username(username)
        self.emoji = self._parse_emoji(emoji)
        self.ping_users = self._parse_ping_users(ping_users)
        self._user_cache: Dict[str, str] = dict()
        self._slacker = slacker.Slacker(api_key)

    @staticmethod
    def _parse_channel(val: Any) -> str:
        channel = str(val)
        if not channel.startswith('#'):
            channel = '#' + channel
        return channel

    @staticmethod
    def _parse_ping_users(val: Any) -> List[str]:
        return [str(item) for item in make_list(val) or []]

    @staticmethod
    def _parse_username(val: Any) -> str:
        return str(val)

    @staticmethod
    def _parse_emoji(val: Any) -> str:
        return str(val)

    def _refresh_user_cache(self) -> None:
        def _helper() -> Any:
            for usr in user_list:
                yield {usr['name']: usr['id']}
                yield {usr['profile']['real_name']: usr['id']}
                yield {usr['profile']['display_name']: usr['id']}

        self.logger.debug("User cache invalidation")
        user_list = self._slacker.users.list().body['members']
        self._user_cache = {k: v for d in _helper() for k, v in d.items()}

    def _lookup_users(self, ping_users: List[str]) -> Iterator[str]:
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

    def _build_message_text(self, text: str, ping_users: List[str]) -> str:
        ping_user_ids = self._lookup_users(ping_users)

        for user_id in ping_user_ids:
            text = "<@{user}> {text}".format(user=user_id, text=text)

        return text

    @Envelope.unwrap
    @Envelope.parse('channel')
    @Envelope.parse('username')
    @Envelope.parse('emoji')
    @Envelope.parse('ping_users')
    def _push_unwrap(
            self, channel: str, username: str, emoji: str,
            ping_users: List[str], envelope: EnvelopeType, payload: Payload
    ) -> Payload:
        text = self._build_message_text(str(payload), ping_users)
        self._slacker.chat.post_message(
            text=text,
            channel=channel,
            username=username,
            icon_emoji=emoji
        )

        return {'data': payload, **envelope} if envelope else payload

    def _push(self, payload: Payload) -> Payload:
        return self._push_unwrap(payload)  # pylint: disable=no-value-for-parameter
