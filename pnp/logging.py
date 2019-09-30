"""Custom logging handler for pnp."""

import traceback
from functools import partial
from logging import (
    Formatter,
    Handler,
    LogRecord,
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    NOTSET,
    WARNING,
    _nameToLevel
)
from typing import Optional, Iterable, Dict, Any, List

import asyncio
import slacker  # type: ignore

ERROR_COLOR = 'danger'  # color name is built in to Slack API
WARNING_COLOR = 'warning'  # color name is built in to Slack API
INFO_COLOR = '#439FE0'

COLORS = {
    CRITICAL: ERROR_COLOR,
    FATAL: ERROR_COLOR,
    ERROR: ERROR_COLOR,
    WARNING: WARNING_COLOR,
    INFO: INFO_COLOR,
    DEBUG: INFO_COLOR,
    NOTSET: INFO_COLOR,
}

DEFAULT_EMOJI = ':robot:'
DEFAULT_USERNAME = 'PnP'
DEFAULT_PING_LEVEL = 'ERROR'


class NoStacktraceFormatter(Formatter):
    """
    By default the stacktrace will be formatted as part of the message.
    Since we want the stacktrace to be in the attachment of the Slack message,
      we need a custom formatter to leave it out of the message.
    """

    def formatException(self, ei: Any) -> Any:
        return None


class SlackerLogHandler(Handler):
    """
    Implements a logging handler that sends formatted messages to slack.
    """

    def __init__(self, api_key: str, channel: str, username: str = DEFAULT_USERNAME,
                 icon_url: Optional[str] = None, icon_emoji: Optional[str] = None,
                 ping_users: Optional[Iterable[str]] = None,
                 ping_level: str = DEFAULT_PING_LEVEL):
        super().__init__()
        self.formatter = NoStacktraceFormatter()
        self.slacker = slacker.Slacker(api_key)
        self.username = str(username)
        self.icon_url = icon_url and str(icon_url)
        self.icon_emoji = icon_emoji if (icon_emoji or icon_url) else DEFAULT_EMOJI
        self.channel = channel
        if not self.channel.startswith('#') and not self.channel.startswith('@'):
            self.channel = '#' + self.channel

        # Optional ping user related stuff
        if str(ping_level).upper() not in _nameToLevel:
            raise ValueError(f"The passed ping_level {str(ping_level)} is not a valid"
                             f"level")
        self.ping_level = _nameToLevel[str(ping_level).upper()]  # type: int
        if not self.ping_level:
            raise ValueError(
                f"Argument ping_level '{ping_level}' is not a valid logging level")
        self.ping_user_ids = []  # type: List[int]

        if ping_users:
            user_map = self._build_user_map()
            for ping_user in ping_users:
                user_id = user_map.get(ping_user)
                if not user_id:
                    raise RuntimeError(
                        'User not found in Slack users list: %s' % ping_user)
                self.ping_user_ids.append(user_id)

    def _build_user_map(self) -> Dict[str, int]:
        def _helper() -> Any:
            for usr in user_list:
                yield {usr['name']: usr['id']}
                yield {usr['profile']['real_name']: usr['id']}
                yield {usr['profile']['display_name']: usr['id']}

        user_list = self.slacker.users.list().body['members']
        return {k: v for d in _helper() for k, v in d.items()}

    def _build_message(self, record: LogRecord) -> str:
        return str(self.format(record))

    def _build_attachment(self, record: LogRecord) -> Dict[str, Any]:
        message = self._build_message(record)
        field = {
            'title': message,
            'short': False
        }
        if record.exc_info:
            trace = '\n'.join(traceback.format_exception(*record.exc_info))
            field['value'] = f"```{trace}```"
        return {
            'color': COLORS.get(record.levelno, INFO_COLOR),
            'fields': [field]
        }

    def emit(self, record: LogRecord) -> None:
        text = ''
        if self.ping_user_ids and record.levelno >= self.ping_level:
            for user in self.ping_user_ids:
                text = f"<@{user}> {text}"

        attachments = [self._build_attachment(record)]

        # Use the executor to fire and forget about the message to post
        # and don't block the workflow just for logging...
        asyncio.get_event_loop().run_in_executor(
            None,
            partial(
                self.slacker.chat.post_message,
                text=text if text != '' else None,
                channel=self.channel,
                username=self.username,
                icon_url=self.icon_url,
                icon_emoji=self.icon_emoji,
                attachments=attachments
            )
        )
