"""Push: http.Call."""

import json
from typing import Any

import requests

from pnp import utils, validator
from pnp.plugins.push import SyncPush, PushExecutionError
from pnp.plugins.push.envelope import Envelope
from pnp.typing import Payload, Envelope as EnvelopeType

CONST_METHOD_DEFAULT = 'GET'


class Call(SyncPush):
    """
    Makes a request to a http resource.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#http-call

    """
    __REPR_FIELDS__ = ['fail_on_error', 'method', 'provide_response', 'url']

    def __init__(
            self, url: str, method: str = CONST_METHOD_DEFAULT, fail_on_error: bool = False,
            provide_response: bool = False, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.url = self._parse_url(url)
        self.method = self._parse_method(method)
        self.fail_on_error = self._parse_fail_on_error(fail_on_error)
        self.provide_response = bool(provide_response)

    @staticmethod
    def _parse_url(val: Any) -> str:
        return str(val)

    @staticmethod
    def _parse_method(val: Any) -> str:
        val_str = str(val).upper()
        validator.one_of(utils.HTTP_METHODS, method=val_str)
        return val_str

    @staticmethod
    def _parse_fail_on_error(val: Any) -> bool:
        return utils.try_parse_bool(val)  # type: ignore

    @Envelope.unwrap
    @Envelope.parse('url')
    @Envelope.parse('method')
    @Envelope.parse('fail_on_error')
    def _push_unwrap(
            self, url: str, method: str, fail_on_error: bool,
            envelope: EnvelopeType, payload: Payload
    ) -> Payload:
        if isinstance(payload, (dict, list, tuple)):
            try:
                payload = json.dumps(payload)
            except:  # pylint: disable=bare-except
                pass
        resp = requests.request(method, url, data=str(payload))
        if fail_on_error and not 200 <= resp.status_code <= 299:
            raise PushExecutionError(
                "{method} of '{url}' failed with status code = '{status_code}'".format(
                    method=method,
                    url=url,
                    status_code=resp.status_code
                )
            )
        if not self.provide_response:
            return {'data': payload, **envelope} if envelope else payload

        try:
            return dict(status_code=resp.status_code, is_json=True, data=resp.json())
        except ValueError:
            # No valid json, try text
            return dict(status_code=resp.status_code, is_json=False, data=resp.text)

    def _push(self, payload: Payload) -> Payload:
        return self._push_unwrap(payload)  # pylint: disable=no-value-for-parameter
