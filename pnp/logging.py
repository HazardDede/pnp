"""Custom logging handler for pnp."""

import asyncio
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

import slacker  # type: ignore
from typeguard import typechecked

from pnp import validator


class NoStacktraceFormatter(Formatter):
    """
    By default the stacktrace will be formatted as part of the message.
    Since we want the stacktrace to be in the attachment of the Slack message,
      we need a custom formatter to leave it out of the message.
    """

    def formatException(self, ei: Any) -> Any:
        return None


class SlackHandler(Handler):
    """
    Implements a logging handler that sends formatted messages to slack.
    """

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
    MAX_ATTACHMENT_CHARS = 1000

    @typechecked
    def __init__(self, api_key: str, channel: str, username: str = DEFAULT_USERNAME,
                 icon_url: Optional[str] = None, icon_emoji: Optional[str] = None,
                 ping_users: Optional[Iterable[str]] = None,
                 ping_level: str = DEFAULT_PING_LEVEL, fire_and_forget: bool = True):
        super().__init__()
        self.formatter = NoStacktraceFormatter()
        self.slacker = slacker.Slacker(api_key)
        self.fire_and_forget = bool(fire_and_forget)
        self.username = str(username)
        self.icon_url = icon_url and str(icon_url)
        self.icon_emoji = icon_emoji if (icon_emoji or icon_url) else self.DEFAULT_EMOJI
        self.channel = channel
        if not self.channel.startswith('#') and not self.channel.startswith('@'):
            self.channel = '#' + self.channel

        # Optional ping user related stuff
        ping_level = str(ping_level).upper()
        validator.one_of(_nameToLevel, ping_level=ping_level)
        self.ping_level = _nameToLevel[ping_level]  # type: int
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
            # Attachments have a character limit. They get truncated by slack
            # automagically, but this will also truncate the code blocks (```).
            # Se we do it on our own and we take the truncate the beginning cause
            # we assume that the end of the trace will contain the mor important
            # information.
            trace_size = len(trace) + 6  # 6 extra chars for backticks
            trace = (trace if trace_size <= self.MAX_ATTACHMENT_CHARS
                     else trace[trace_size - self.MAX_ATTACHMENT_CHARS:])
            field['value'] = "```{trace}```".format(trace=trace)
        return {
            'color': self.COLORS.get(record.levelno, self.INFO_COLOR),
            'fields': [field]
        }

    def emit(self, record: LogRecord) -> None:
        text = ''
        if self.ping_user_ids and record.levelno >= self.ping_level:
            for user in self.ping_user_ids:
                text = "<@{user}> {text}".format(user=user, text=text)

        attachments = [self._build_attachment(record)]

        # Use the executor to fire and forget about the message to post
        # and don't block the workflow just for logging...
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        slacker_call = partial(
            self.slacker.chat.post_message,
            text=text if text != '' else None,
            channel=self.channel,
            username=self.username,
            icon_url=self.icon_url,
            icon_emoji=self.icon_emoji,
            attachments=attachments
        )
        if self.fire_and_forget:
            loop.run_in_executor(None, slacker_call)  # Don't wait and don't check errors
        else:
            slacker_call()  # Wait for the call to finish; this will block asyncio
