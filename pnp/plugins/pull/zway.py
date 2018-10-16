import re

import requests
import schema
from requests.auth import HTTPBasicAuth

from . import Polling, PollingError
from .http import Server
from ...utils import auto_str_ignore, try_parse_int_float_str
from ...validator import Validator


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


class ZwayReceiver(Server):
    """
    Setups a http server to process incoming GET-requests from the
    Zway-App [`HttpGet`](https://github.com/hplato/Zway-HTTPGet/blob/master/index.js).

    Besides the arguments noted below the component will accept any arguments that `pnp.plugins.pull.http.Server`
    would accept.

    Args:
        url_format (str): The url_format that is configured in your HttpGet App. If you configured
            `http://<ip>:<port>/set?device=%DEVICE%&state=%VALUE%` (default of the App), you basically have to copy
            the path component `set?device=%DEVICE%&state=%VALUE%` to be your `url_format`.
        device_mapping (Union[Dict[Str, Str], Dict[Str, Dict]], optional): A mapping to map the somewhat cryptic
            virtual device names to human readable ones. Default is None, which means that no mapping will be performed.
            Two ways possible:
                1. Ordinary mapping from virtual device name -> alias.
                2. Enhanced mapping from virtual device name to dictionary with additional properties. One property
                has to be alias.
        ignore_unknown_devices (bool, optional): If set to True all incoming requests that are associated with an
            device that is not part of the mapping will be ignored. Default is False.<br/>

    Returns:

        Given the url_format `%DEVICE%?value=%VALUE%`, the url `http://<ip>:<port>/set?vdevice1?value=5.5` and
        the device_mapping `vdevice1 -> alias of vdevice1` the emitted message will look like this:

        ```yaml
        {
            'device_name': 'alias of vdevice1',
            'raw_device': 'vdevice1'
            'value': 5.5,
            'props': {}
        }
        ```
    """
    MAPPING_SCHEMA = schema.Schema({
        schema.Optional(str): schema.Or(
            {
                'alias': schema.Use(str),
                schema.Optional(str): object
            },
            schema.Use(lambda val: dict(alias=val, props={}))
        )
    })

    DEVICE_REGEX = r'[a-zA-Z0-9_\-]+'
    VALUE_REGEX = r'[a-zA-Z0-9\.,]+'

    @staticmethod
    def _make_regex(url_format):
        escaped_url = re.escape(url_format)
        device_group = "(?P<device>{})".format(ZwayReceiver.DEVICE_REGEX)
        value_group = "(?P<value>{})".format(ZwayReceiver.VALUE_REGEX)
        return re.compile('.*' + escaped_url.replace('\%DEVICE\%', device_group).replace('\%VALUE\%', value_group)
                          .replace('%DEVICE%', device_group).replace('%VALUE%', value_group))

    @staticmethod
    def _safe_get_group(match, group_name):
        try:
            return match.group[group_name]
        except IndexError:
            return None

    def __init__(self, url_format="/set?device=%DEVICE%&state=%VALUE%", device_mapping=None,
                 ignore_unknown_devices=False, **kwargs):
        # Zway module HttpGet only supports GET calls
        kwargs['allowed_methods'] = 'GET'
        super().__init__(**kwargs)
        self.ignore_unknown_devices = bool(ignore_unknown_devices)

        Validator.is_instance(str, url_format=url_format)
        if not url_format.startswith('/'):
            url_format = '/' + url_format
        if '?' not in url_format:
            url_format = url_format + '?'
        self.url_format = url_format
        self.url_format_regex = self._make_regex(url_format)

        if device_mapping is None:
            device_mapping = {}
        self.device_mapping = self.MAPPING_SCHEMA.validate(device_mapping)

    def notify(self, payload):
        full_path = payload['full_path']
        match = self.url_format_regex.match(full_path)
        if match is None:
            self.logger.warn("Cannot extract device_name and/or value from '{}' with regex '{}'".format(
                full_path, self.url_format_regex
            ))
            return
        raw_device = match.group('device')
        value = match.group('value')

        device_map = self.device_mapping.get(raw_device)
        if device_map is None:
            if self.ignore_unknown_devices:
                self.logger.debug("Got device '{raw_device}' but it is ignored".format(**locals()))
                return  # Device is not mapped and should be ignored-> abort
            device_map = dict(alias=raw_device)  # If it isn't ignored just take the raw name

        device_map = device_map.copy()
        alias = device_map.pop('alias')
        super().notify(dict(device_name=alias, props=device_map, raw_device=raw_device,
                            value=try_parse_int_float_str(value)))
