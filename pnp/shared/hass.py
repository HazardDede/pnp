"""Home assistant related utility classes."""

import json
import urllib.parse as urlparse
from typing import Any, Optional

from typeguard import typechecked

from pnp.utils import ReprMixin


class HassApi(ReprMixin):
    """Utility class to communicate with home assistant via the rest-api."""

    METHOD_GET = 'get'
    METHOD_POST = 'post'
    ALLOWED_METHODS = [METHOD_GET, METHOD_POST]

    __REPR_FIELDS__ = ["base_url", "timeout"]

    @typechecked
    def __init__(self, base_url: str, token: str, timeout: Optional[int] = None):
        self.base_url = base_url
        self.token = token
        self.timeout = timeout and int(timeout)

    @typechecked
    def call(self, endpoint: str, method: str = METHOD_GET, data: Any = None) -> Any:
        """Calls the specified endpoint (without prefix api) using the given method.
        You can optionally pass data to the request which will be json encoded."""
        from requests import get, post

        method = str(method).lower()
        if method not in self.ALLOWED_METHODS:
            raise ValueError(
                "Argument method is expected to be one of {allowed}, but is '{method}'".format(
                    allowed=str(self.ALLOWED_METHODS),
                    method=method)
            )

        url = urlparse.urljoin(urlparse.urljoin(self.base_url, 'api/'), endpoint)
        headers = {
            'Authorization': 'Bearer {self.token}'.format(**locals()),
            'content-type': 'application/json',
        }

        if data is not None:
            data = json.dumps(data)

        if method == self.METHOD_GET:
            response = get(url, headers=headers, timeout=self.timeout, data=data)
        else:
            response = post(url, headers=headers, timeout=self.timeout, data=data)

        if response.status_code != 200:
            raise RuntimeError("Failed to call endpoint {url}"
                               "\nHttp Code: {response.status_code}"
                               "\nMessage: {response.text}".format(**locals()))

        return response.json()
