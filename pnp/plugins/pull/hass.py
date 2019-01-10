import asyncio
import json

import asyncws

from . import PullBase
from ...utils import make_list, auto_str_ignore, include_or_exclude, wildcards_to_regex


@auto_str_ignore(['token', '_websocket', '_loop', '_include_regex', '_exclude_regex'])
class State(PullBase):
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

    def _layout_message(self, message):
        def _layout_state(state):
            from copy import copy
            cp = copy(state)
            cp.pop('entity_id', None)
            cp.pop('context', None)
            return cp

        state_data = message.get('event', {}).get('data', {})
        entity_id = state_data.get('entity_id')
        old_state = _layout_state(state_data.get('old_state', {}))
        new_state = _layout_state(state_data.get('new_state', {}))
        return {'entity_id': entity_id, 'old_state': old_state, 'new_state': new_state}

    def _emit(self, message):
        payload = self._layout_message(message)
        if include_or_exclude(payload['entity_id'], self._include_regex, self._exclude_regex):
            self.on_payload(self, payload)

    async def _receive_states(self):
        self._websocket = await asyncws.connect('{self.url}/api/websocket'.format(**locals()))

        while True:
            message = await self._websocket.recv()
            if message is None:
                break
            message = json.loads(message)
            if message.get('type', '') == 'auth_required':
                hass_version = message.get('ha_version')
                self.logger.info("[{self.name}] Connected to Home Assistant {hass_version} websocket @ {self.url}"
                                 .format(**locals()))
                self.logger.debug("[{self.name}] Authentication is required. Providing token".format(**locals()))
                await self._websocket.send(json.dumps({
                    'type': 'auth',
                    'access_token': self.token
                }))
            elif message.get('type', '') == 'auth_ok':
                self.logger.info("[{self.name}] Authentication is valid".format(**locals()))
                await self._websocket.send(json.dumps(
                    {'id': 1, 'type': 'subscribe_events', 'event_type': 'state_changed'}
                ))
            elif message.get('type', '') == 'auth_invalid':
                self.logger.info("[{self.name}] Authentication is invalid. Aborting...".format(**locals()))
                await self._websocket.close()
            elif message.get('type', '') == 'result':
                pass
            elif message.get('type', '') == 'event':
                self._emit(message)
            else:
                self.logger.warning("[{self.name}] Got unexpected message '{message}'".format(**locals()))

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
