import json

import requests

from ...utils import try_parse_bool
from ...validator import Validator
from ... import utils
from . import PushBase, PushExecutionError


class Call(PushBase):

    def __init__(self, url, method='GET', fail_on_error=False, provide_response=False, **kwargs):
        super().__init__(**kwargs)
        self.url = self._parse_url(url)
        self.method = self._parse_method(method)
        self.fail_on_error = self._parse_fail_on_error(fail_on_error)
        self.provide_response = bool(provide_response)

    def _parse_url(self, val):
        return str(val)

    def _parse_method(self, val):
        val = str(val).upper()
        Validator.one_of(utils.HTTP_METHODS, method=val)
        return val

    def _parse_fail_on_error(self, val):
        return try_parse_bool(val)

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)

        url = self._parse_envelope_value('url', envelope)
        method = self._parse_envelope_value('method', envelope)
        fail_on_error = self._parse_envelope_value('fail_on_error', envelope)

        if isinstance(real_payload, (dict, list, tuple)):
            try:
                real_payload = json.dumps(real_payload)
            except:
                pass
        resp = requests.request(method, url, data=str(real_payload))
        if fail_on_error and not (200 <= resp.status_code <= 299):
            raise PushExecutionError("{method} of '{url}' failed with "
                                     "status code = '{resp.status_code}'".format(**locals()))
        if not self.provide_response:
            return payload

        try:
            return dict(status_code=resp.status_code, is_json=True, data=resp.json())
        except ValueError:
            # No valid json, try text
            return dict(status_code=resp.status_code, is_json=False, data=resp.text)
