"""Z-Way related pulls."""

import requests
from requests.auth import HTTPBasicAuth

from pnp.plugins.pull import PollingError, SyncPolling


class ZwayPoll(SyncPolling):
    """
    Pulls the specified json content from the z-way rest api.
    The content is specified by the url, e.g. http://<host>:8083/ZWaveAPI/Run/devices will pull
    all devices and serve the result as a json.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#zway-zwaypoll
    """

    __REPR_FIELDS__ = ['url', 'user']

    def __init__(self, url, user, password, **kwargs):
        super().__init__(**kwargs)
        self.url = str(url)
        self.user = str(user)
        self.password = str(password)

    def _poll(self):
        self.logger.debug("Polling url '%s'", self.url)
        reply = requests.get(self.url, auth=HTTPBasicAuth(self.user, self.password))
        if reply.status_code != requests.codes.ok:  # pylint: disable=no-member
            raise PollingError(
                "Code {code}: {error}".format(code=reply.status_code, error=reply.text)
            )

        try:
            return reply.json()
        except ValueError:
            # No valid json, try text
            return reply.text
