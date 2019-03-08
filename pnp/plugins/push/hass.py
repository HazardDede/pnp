"""Home assistant related push plugins"""

from . import PushBase
from ...shared.hass import HassApi
from ...utils import auto_str_ignore


@auto_str_ignore(['_client', 'token'])
class Service(PushBase):
    """
    Calls a home assistant service providing the payload as service-data.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/hass.Service/index.md
    """
    __prefix__ = 'hass'

    def __init__(self, url, token, domain, service, timeout=10, **kwargs):
        super().__init__(**kwargs)
        self.url = str(url)
        self.token = str(token)
        self.domain = str(domain)
        self.service = str(service)
        self.timeout = timeout and int(timeout)
        if self.timeout <= 0:
            self.timeout = None  # Basically means no timeout
        self._client = HassApi(self.url, self.token, self.timeout)

    def _call(self, data):
        endpoint = 'services/{self.domain}/{self.service}'.format(**locals())

        try:
            return self._client.call(endpoint, method='post', data=data)
        except RuntimeError as exc:
            raise RuntimeError(
                "Failed to call the service {endpoint} @ {self.url}".format(**locals())
            ) from exc

    def push(self, payload):
        self._call(payload)
        return payload
