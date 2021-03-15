"""Fitbit shared utility stuff."""

import os
import pathlib
from typing import Any, Optional, Dict

import fitbit
import schema
from ruamel import yaml

from pnp import validator
from pnp.plugins.pull import AsyncPolling
from pnp.typing import Payload
from pnp.utils import FileLock


PathLike = str
FitbitSystem = str
Tokens = Dict[str, Any]


_TOKEN_SCHEMA = schema.Schema({
    'client_id': schema.Use(str),
    'client_secret': schema.Use(str),
    'access_token': schema.Use(str),
    'refresh_token': schema.Use(str),
    'expires_at': schema.Use(float)
})


class FitbitBase(AsyncPolling):
    """Fitbit base class. Implements the token management."""

    __REPR_FIELDS__ = ['config', 'system']

    def __init__(self, config: PathLike, system: Optional[FitbitSystem] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.system = system

        # Absolute config path? Relative -> relative to pnp configuration file
        self.config = config
        if not os.path.isabs(config):
            self.config = os.path.join(self.base_path, config)
        validator.is_file(config=self.config)

        import threading
        self._client_lock = threading.Lock()
        self._tokens: Optional[Tokens] = None  # Set by _load_tokens
        self._tokens_tstamp: Optional[float] = None  # Set by _load_tokens and _save_tokens
        self._client: Optional[fitbit.Fitbit] = None  # Set by client property

    @property
    def client(self) -> fitbit.Fitbit:
        """Return the configured fitbit client."""
        with self._client_lock:
            if self._load_tokens():  # Check if tokens got refreshed by another process
                self._client = fitbit.Fitbit(
                    **self._tokens, oauth2=True,
                    refresh_cb=self._save_tokens, system=self.system
                )
            return self._client

    def _load_tokens(self) -> bool:
        current_tstamp = pathlib.Path(self.config).stat().st_mtime
        # Compare memorized modified timestamp (might be None initially) and current
        if self._tokens_tstamp == current_tstamp:
            # Tokens did not change. Skip
            return False

        self.logger.debug("Loading tokens from %s: Requesting lock", self.config)
        with FileLock(self.config):
            self.logger.debug("Loading tokens from %s: Lock acquired", self.config)
            with open(self.config, 'r') as fp:
                _tokens = yaml.safe_load(fp)
                self._tokens = _TOKEN_SCHEMA.validate(_tokens)
            self._tokens_tstamp = current_tstamp
        self.logger.debug("Loading tokens from %s: Lock released", self.config)
        return True

    def _save_tokens(self, tokens: Tokens) -> None:
        assert self._tokens, "No tokens present. Should not happen in production"
        new_config = {
            'client_id': self._tokens.get('client_id'),
            'client_secret': self._tokens.get('client_secret'),
            'access_token': tokens.get('access_token'),
            'refresh_token': tokens.get('refresh_token'),
            'expires_at': tokens.get('expires_at')
        }
        self.logger.debug("Saving tokens to %s: Requesting lock", self.config)
        _TOKEN_SCHEMA.validate(new_config)
        with FileLock(self.config):
            self.logger.debug("Saving tokens to %s: Lock acquired", self.config)
            with open(self.config, 'w') as fp:
                yaml.dump(new_config, fp, default_flow_style=False)
            self._tokens_tstamp = pathlib.Path(self.config).stat().st_mtime
            self._tokens = new_config
            self.logger.debug("Saving tokens to %s: Lock released", self.config)

    async def _poll(self) -> Payload:
        raise NotImplementedError()  # pragma: no cover
