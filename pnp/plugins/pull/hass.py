"""Home assistant related plugins."""

import asyncio
import json

import asyncws

from . import PullBase
from ...utils import make_list, auto_str_ignore, include_or_exclude, wildcards_to_regex


@auto_str_ignore(['token', '_websocket', '_loop', '_include_regex', '_exclude_regex'])
class State(PullBase):
    """
    Connects to the home assistant websocket api and listens for state changes.
    If no include or exclude is defined it will report all state changes.
    If include is defined only entities that match one of the specified patterns will be emitted.
    If exclude if defined entities that match at least one of the specified patterns will
    be ignored. Exclude patterns overrides include patterns.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/hass.State/index.md
    """
    __prefix__ = 'hass'

    def __init__(self, url, token, include=None, exclude=None, **kwargs):
        super().__init__(**kwargs)
        self.url = self._sanitize_url(url)
        self.token = str(token)
        self.include = make_list(include)
        self.exclude = make_list(exclude)
        self._websocket = None
        self._loop = None

        self._include_regex = self.include and wildcards_to_regex(self.include)
        self._exclude_regex = self.exclude and wildcards_to_regex(self.exclude)

    @staticmethod
    def _sanitize_url(url):
        res = str(url).replace('https://', 'wss://').replace('http://', 'ws://')
        if res.endswith('/'):
            return res[:-1]  # Remove last /
        return res

    @staticmethod
    def _layout_message(message):
        def _layout_state(state):
            from copy import copy
            _copy = copy(state)
            _copy.pop('entity_id', None)
            _copy.pop('context', None)
            return _copy

        state_data = message.get('event', {}).get('data', {})
        entity_id = state_data.get('entity_id')
        old_state = _layout_state(state_data.get('old_state', {}))
        new_state = _layout_state(state_data.get('new_state', {}))
        return {'entity_id': entity_id, 'old_state': old_state, 'new_state': new_state}

    def _emit(self, message):
        payload = self._layout_message(message)
        if include_or_exclude(payload['entity_id'], self._include_regex, self._exclude_regex):
            self.on_payload(self, payload)  # pylint: disable=too-many-function-args

    async def _receive_states(self):
        self._websocket = await asyncws.connect('{self.url}/api/websocket'.format(**locals()))

        while True:
            message = await self._websocket.recv()
            if message is None:
                break
            message = json.loads(message)
            if message.get('type', '') == 'auth_required':
                hass_version = message.get('ha_version')
                self.logger.info(
                    "[%s] Connected to Home Assistant %s websocket @ %s",
                    self.name, hass_version, self.url
                )
                self.logger.debug("[%s] Authentication is required. Providing token", self.name)
                await self._websocket.send(json.dumps({
                    'type': 'auth',
                    'access_token': self.token
                }))
            elif message.get('type', '') == 'auth_ok':
                self.logger.info("[%s] Authentication is valid", self.name)
                await self._websocket.send(json.dumps(
                    {'id': 1, 'type': 'subscribe_events', 'event_type': 'state_changed'}
                ))
            elif message.get('type', '') == 'auth_invalid':
                self.logger.info("[%s] Authentication is invalid. Aborting...", self.name)
                await self._websocket.close()
            elif message.get('type', '') == 'result':
                pass
            elif message.get('type', '') == 'event':
                self._emit(message)
            else:
                self.logger.warning("[%s] Got unexpected message '%s'", self.name, message)

    def stop(self):
        super().stop()
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._websocket.close(), self._loop)

    def pull(self):
        try:
            self._loop = asyncio.get_event_loop()
            is_new = False
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            is_new = True
        try:
            self._loop.run_until_complete(self._receive_states())
        finally:
            if is_new:
                self._loop.close()
            self._loop = None
            self._websocket = None
