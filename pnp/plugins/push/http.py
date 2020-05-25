"""Http related push plugins."""

import json

import requests

from pnp import utils
from pnp import validator
from pnp.plugins.push import PushBase, PushExecutionError, enveloped, parse_envelope


class Call(PushBase):
    """
    Makes a request to a http resource.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/http.Call/index.md

    """
    def __init__(self, url, method='GET', fail_on_error=False, provide_response=False, **kwargs):
        super().__init__(**kwargs)
        self.url = self._parse_url(url)
        self.method = self._parse_method(method)
        self.fail_on_error = self._parse_fail_on_error(fail_on_error)
        self.provide_response = bool(provide_response)

    @staticmethod
    def _parse_url(val):
        return str(val)

    @staticmethod
    def _parse_method(val):
        val = str(val).upper()
        validator.one_of(utils.HTTP_METHODS, method=val)
        return val

    @staticmethod
    def _parse_fail_on_error(val):
        return utils.try_parse_bool(val)

    @enveloped
    @parse_envelope('url')
    @parse_envelope('method')
    @parse_envelope('fail_on_error')
    def push(self, url, method, fail_on_error, envelope, payload):  # pylint: disable=arguments-differ
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
