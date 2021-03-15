"""Pull: hass.State."""

import json
from typing import Iterable, Union, Optional, Any, Dict

import asyncws
from pydantic import BaseModel

from pnp.plugins.pull import AsyncPull
from pnp.utils import make_list, include_or_exclude, wildcards_to_regex


HassRawStateEvent = Dict[str, Any]
IncludeExclude = Union[Iterable[str], str]
StateChange = Dict[str, Any]


class HassStateEvent(BaseModel):
    """Represents a home assistant state event."""

    entity_id: str
    old_state: StateChange
    new_state: StateChange

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    @classmethod
    def from_raw(cls, raw_message: HassRawStateEvent) -> 'HassStateEvent':
        """Parses a raw home assistant state messages into this representation."""
        def _parse_state(state: HassRawStateEvent) -> HassRawStateEvent:
            from copy import copy
            _copy = copy(state)
            _copy.pop('entity_id', None)
            _copy.pop('context', None)
            return _copy

        state_data = raw_message.get('event', {}).get('data', {})
        entity_id = state_data.get('entity_id')
        old_state = _parse_state(state_data.get('old_state', {}))
        new_state = _parse_state(state_data.get('new_state', {}))

        return cls(entity_id=entity_id, old_state=old_state, new_state=new_state)


class State(AsyncPull):
    """
    Connects to the home assistant websocket api and listens for state changes.
    If no include or exclude is defined it will report all state changes.
    If include is defined only entities that match one of the specified patterns will be emitted.
    If exclude if defined entities that match at least one of the specified patterns will
    be ignored. Exclude patterns overrides include patterns.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#hass-state
    """
    __REPR_FIELDS__ = ['exclude', 'include', 'url']

    def __init__(
            self, url: str, token: str, include: Optional[IncludeExclude] = None,
            exclude: Optional[IncludeExclude] = None, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.url = self._sanitize_url(url)
        self.token = str(token)
        self.include = make_list(include)
        self.exclude = make_list(exclude)
        self._websocket = None

        self._include_regex = self.include and wildcards_to_regex(self.include)
        self._exclude_regex = self.exclude and wildcards_to_regex(self.exclude)

    @staticmethod
    def _sanitize_url(url: str) -> str:
        res = str(url).replace('https://', 'wss://').replace('http://', 'ws://')
        if res.endswith('/'):
            return res[:-1]  # Remove last /
        return res

    async def _emit(self, message: HassRawStateEvent) -> None:
        state_event = HassStateEvent.from_raw(message)
        if include_or_exclude(state_event.entity_id, self._include_regex, self._exclude_regex):
            self.notify(state_event.dict())

    async def _receive_states(self) -> None:
        self._websocket = await asyncws.connect('{self.url}/api/websocket'.format(**locals()))
        assert self._websocket

        while True:
            message = await self._websocket.recv()
            if message is None:
                await self._websocket.close()
                self._websocket = None
                break
            message = json.loads(message)
            if message.get('type', '') == 'auth_required':
                hass_version = message.get('ha_version')
                self.logger.info(
                    "Connected to Home Assistant %s websocket @ %s",
                    hass_version, self.url
                )
                self.logger.debug("Authentication is required. Providing token")
                await self._websocket.send(json.dumps({
                    'type': 'auth',
                    'access_token': self.token
                }))
            elif message.get('type', '') == 'auth_ok':
                self.logger.info("Authentication is valid")
                await self._websocket.send(json.dumps(
                    {'id': 1, 'type': 'subscribe_events', 'event_type': 'state_changed'}
                ))
            elif message.get('type', '') == 'auth_invalid':
                self.logger.info("Authentication is invalid. Aborting...")
                await self._websocket.close()
            elif message.get('type', '') == 'result':
                pass
            elif message.get('type', '') == 'event':
                await self._emit(message)
            else:
                self.logger.warning("Got unexpected message '%s'", message)

    async def _stop(self) -> None:
        await super()._stop()
        if self._websocket:
            await self._websocket.close()

    async def _pull(self) -> None:
        await self._receive_states()
