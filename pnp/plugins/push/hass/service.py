"""Home assistant related push plugins"""
from typing import Any, Optional

from pnp.plugins.push import SyncPush
from pnp.shared.hass import HassApi
from pnp.typing import Payload


class Service(SyncPush):
    """
    Calls a home assistant service providing the payload as service-data.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#hass-service
    """

    __REPR_FIELDS__ = ['domain', 'service', 'timeout', 'url']

    def __init__(
            self, url: str, token: str, domain: str, service: str,
            timeout: Optional[int] = 10, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.url = str(url)
        self.token = str(token)
        self.domain = str(domain)
        self.service = str(service)
        self.timeout = timeout and int(timeout)
        if self.timeout is None or self.timeout <= 0:
            self.timeout = None  # Basically means no timeout
        self._client = HassApi(self.url, self.token, self.timeout)

    def _push(self, payload: Payload) -> Payload:
        endpoint = 'services/{domain}/{service}'.format(
            domain=self.domain,
            service=self.service
        )

        try:
            return self._client.call(endpoint, method='post', data=payload)
        except RuntimeError as exc:
            raise RuntimeError(
                "Failed to call the service {endpoint} @ {url}".format(
                    endpoint=endpoint,
                    url=self.url
                )
            ) from exc
