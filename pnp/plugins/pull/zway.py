import requests
from requests.auth import HTTPBasicAuth

from . import Polling, PollingError
from ...utils import auto_str_ignore


@auto_str_ignore(['password'])
class ZwayPoll(Polling):
    __prefix__ = 'zway'

    def __init__(self, url, user, password, **kwargs):
        super().__init__(**kwargs)
        self.url = str(url)
        self.user = str(user)
        self.password = str(password)

    def poll(self):
        self.logger.debug("[{name}] Polling url '{url}'".format(name=self.name, url=self.url))
        reply = requests.get(self.url, auth=HTTPBasicAuth(self.user, self.password))
        if reply.status_code != requests.codes.ok:
            raise PollingError("Code {code}: {error}".format(code=reply.status_code, error=reply.text))

        try:
            return reply.json()
        except ValueError:
            # No valid json, try text
            return reply.text
