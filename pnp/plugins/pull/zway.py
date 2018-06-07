import requests
from requests.auth import HTTPBasicAuth

from . import Polling, PollingError
from ...utils import auto_str_ignore


@auto_str_ignore(['password'])
class ZwayPoll(Polling):
    """
    Pulls the specified json content from the zway rest api. The content is specified by the url, e.g.
    `http://<host>:8083/ZWaveAPI/Run/devices` will pull all devices and serve the result as a json.

    Specify the polling interval by setting the argument `interval`. User / password combination is required when
    your api is protected against guest access (by default it is).

    Use multiple pushes and the related selectors to extract the required content like temperature readings (see
    the example configuration for guidance).

    All arguments (`url`, `user` and `password`) can be automatically injected via environment variables.
    * ZWAY_URL
    * ZWAY_USER
    * ZWAY_PASSWORD

    Args:
        url (str): The zway api url to poll.
        user (str): The user for authentication to the api.
        password (str): The related password.

    Returns:
        The `on_payload` callback will pass the result of specified url.

    Example configuration:

        name: zway
        pull:
          plugin: pnp.plugins.pull.ZwayPoll
          args:
            url: http://<host>:8083/ZWaveAPI/Run/devices  # Retrieve all devices
            user: admin
            password: secret
            interval: 5m  # Poll the api every 5 minutes
        push:
          - plugin: pnp.plugins.push.Echo
            selector: payload[19].instances[0].commandClasses[49].data[1].val.value  # temp. of fibaro motion sensor
          - plugin: pnp.plugins.push.Echo
            selector: payload[9].instances[0].commandClasses[128].data.last.value  # Setpoint of heater

    """

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
