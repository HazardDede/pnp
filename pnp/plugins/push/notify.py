"""Notification related push plugins."""

from typing import Any, Dict, List, Optional

import slacker

from pnp.plugins import load_optional_module
from pnp.plugins.push import PushBase, enveloped, parse_envelope
from pnp.typing import Envelope, Payload
from pnp.utils import auto_str_ignore, make_list


@auto_str_ignore(['api_key'])
class Pushbullet(PushBase):
    """
    Sends a message to the Pushbullet service. The type of the message will guessed:

    - `push_link` for a single http link
    - `push_file` if the link is directed to a file (mimetype will be guessed)
    - `push_note` for everything else (converted to str)

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/notify.Pushbullet/index.md
    """
    EXTRA = 'pushbullet'

    def __init__(self, api_key, title='pnp', **kwargs):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.title = str(title)

    def _load_deps(self):
        pbullet = load_optional_module('pushbullet', self.EXTRA)
        try:
            import urlparse
        except:  # For Python 3, pylint: disable=bare-except
            import urllib.parse as urlparse

        return pbullet, urlparse

    def _guess_mimetype(self, url):
        import mimetypes
        _, urlparse = self._load_deps()
        res = urlparse.urlparse(url)
        if not res.path:
            return None
        mtype, _ = mimetypes.guess_type(res.path)
        return mtype

    @staticmethod
    def _safe_basename(name):
        import os
        try:
            return os.path.basename(name)
        except:  # pylint: disable=bare-except
            return name

    @enveloped
    def push(self, envelope, payload):  # pylint: disable=arguments-differ
        pbullet, urlparse = self._load_deps()
        client = pbullet.Pushbullet(self.api_key)
        urlprofile = urlparse.urlparse(payload)
        self.logger.info("Sending message '%s' to Pushbullet", payload)
        if urlprofile.scheme and urlprofile.netloc:
            # Is URL
            self.logger.debug("Payload '%s' is an url", payload)
            mtype = self._guess_mimetype(payload)
            if not mtype:
                # Some link
                self.logger.debug(
                    "Payload '%s' has no mimetype associated", payload
                )
                client.push_link(self.title, payload)
            else:
                # Some file
                self.logger.debug(
                    "Guessed type '%s' for payload '%s'", mtype, payload
                )
                client.push_file(
                    file_name=self._safe_basename(urlprofile.path),
                    file_type=mtype,
                    file_url=payload,
                    title=self.title
                )
        else:
            # Is NOT url
            self.logger.debug("Payload '%s' is a simple note", payload)
            client.push_note(self.title, payload)

        return {'data': payload, **envelope} if envelope else payload


@auto_str_ignore(['api_key', '_slacker', '_user_cache'])
class Slack(PushBase):
    """
    Sends a message to slack. Optionally you can specify users to ping.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/notify.Slack/index.md
    """
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
    def push(self, channel: str, username: str, emoji: str,  # pylint: disable=arguments-differ
             ping_users: List[str], envelope: Envelope, payload: Payload):

        text = self._build_message_text(str(payload), ping_users)
        self._slacker.chat.post_message(
            text=text,
            channel=channel,
            username=username,
            icon_emoji=emoji
        )

        return {'data': payload, **envelope} if envelope else payload
