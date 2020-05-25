"""Z-Way related pulls."""

import re

import requests
import schema
from requests.auth import HTTPBasicAuth

from pnp import validator
from pnp.plugins.pull import Polling, PollingError
from pnp.plugins.pull.http import Server
from pnp.utils import auto_str_ignore, try_parse_int_float_str


@auto_str_ignore(['password'])
class ZwayPoll(Polling):
    """
    Pulls the specified json content from the z-way rest api.
    The content is specified by the url, e.g. http://<host>:8083/ZWaveAPI/Run/devices will pull
    all devices and serve the result as a json.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/zway.ZwayPoll/index.md
    """

    def __init__(self, url, user, password, **kwargs):
        super().__init__(**kwargs)
        self.url = str(url)
        self.user = str(user)
        self.password = str(password)

    def poll(self):
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


class ZwayReceiver(Server):
    """
    Setups a http server to process incoming GET-requests from the
    Z-Way-App [`HttpGet`](https://github.com/hplato/Zway-HTTPGet/blob/master/index.js).

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/zway.ZwayReceiver/index.md
    """
    ZWAY_PATH_PREFIX = 'zway'

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
    MODE_AUTO = 'auto'
    MODE_MAPPING = 'mapping'
    MODE_BOTH = 'both'
    VALID_MODES = [MODE_AUTO, MODE_MAPPING, MODE_BOTH]
    VDEV_REGEX = r'ZWayVDev_zway_(?P<device_id>[0-9]+)\-(?P<instance>[0-9]+)\-(?P<cclass>[0-9]+)' \
                 r'(\-(?P<mode>[0-9]+))?'

    AUTO_MAPPING = {
        '37': 'switch',  # Switch binary
        '38': 'level',  # Switch multilevel
        '48': {'1': 'motion'},  # Sensor binary
        '49': {'1': 'temperature', '3': 'illumination', '4': 'power'},  # Sensor multilevel
        '50': {'0': 'consumption'},  # Meter
        '67': {'1': 'setpoint'},  # Thermostat
        '128': 'battery'
    }

    @staticmethod
    def _make_regex(url_format):
        escaped_url = re.escape(url_format)
        device_group = "(?P<device>{})".format(ZwayReceiver.DEVICE_REGEX)
        value_group = "(?P<value>{})".format(ZwayReceiver.VALUE_REGEX)
        return re.compile(
            '.*' + escaped_url.replace(r'\%DEVICE\%', device_group)
            .replace(r'\%VALUE\%', value_group)
            .replace(r'%DEVICE%', device_group)
            .replace(r'%VALUE%', value_group)
        )

    @staticmethod
    def _safe_get_group(match, group_name):
        try:
            return match.group[group_name]
        except IndexError:
            return None

    @classmethod
    def _auto_map(cls, cclass, mode):
        descr = cls.AUTO_MAPPING.get(str(cclass))
        if not descr:
            return None
        if isinstance(descr, dict) and mode:
            descr = descr.get(str(mode))
        return descr

    def __init__(
            self, device_mapping=None, ignore_unknown_devices=False, mode='mapping',
            vdev_regex=None, **kwargs
    ):
        # Zway module HttpGet only supports GET calls
        kwargs['allowed_methods'] = 'GET'
        kwargs['prefix_path'] = self.ZWAY_PATH_PREFIX
        super().__init__(**kwargs)
        self.ignore_unknown_devices = bool(ignore_unknown_devices)

        self.url_format = "/{}?device=%DEVICE%&value=%VALUE%".format(self.ZWAY_PATH_PREFIX)
        self.url_format_regex = self._make_regex(self.url_format)

        if device_mapping is None:
            device_mapping = {}
        self.device_mapping = self.MAPPING_SCHEMA.validate(device_mapping)

        validator.one_of(self.VALID_MODES, mode=mode)
        self.mode = mode

        if mode in [self.MODE_BOTH, self.MODE_AUTO]:
            self._vdev_regex = vdev_regex or self.VDEV_REGEX
            self._vdev_regex_compiled = re.compile(self.VDEV_REGEX)

    def notify(self, payload):
        full_path = payload['full_path']
        match = self.url_format_regex.match(full_path)
        if match is None:
            self.logger.warning(
                "Cannot extract device_name and/or value from '%s' with regex '%s'",
                full_path, self.url_format_regex
            )
            return
        raw_device = match.group('device')
        value = match.group('value')

        device_map = None
        if self.mode in [self.MODE_MAPPING, self.MODE_BOTH]:
            device_map = self.device_mapping.get(raw_device)

        if not device_map and self.mode in [self.MODE_AUTO, self.MODE_BOTH]:
            match = self._vdev_regex_compiled.match(raw_device)

            if match is not None:
                device_id, cclass, mode = (
                    match.group('device_id'),
                    match.group('cclass'),
                    match.group('mode')
                )
                type_of_device = self._auto_map(cclass, mode)
                if not type_of_device and self.ignore_unknown_devices:
                    self.logger.debug(
                        "Got device '%s' but it is unknown to the automapper", raw_device
                    )
                    return
                device_map = {
                    'alias': device_id,
                    'command_class': cclass,
                    'mode': mode,
                    'type': type_of_device or (cclass + '-{}'.format(mode) if mode else '')
                }
            else:
                self.logger.warning(
                    "Cannot extract device_name and/or value from '%s' with regex '%s'",
                    raw_device, self._vdev_regex
                )

        if device_map is None:
            if self.ignore_unknown_devices:
                self.logger.debug("Got device '%s' but it is ignored", raw_device)
                return  # Device is not mapped and should be ignored-> abort
            device_map = dict(alias=raw_device)  # If it isn't ignored just take the raw name

        device_map = device_map.copy()
        alias = device_map.pop('alias')
        super().notify(dict(
            device_name=alias,
            props=device_map,
            raw_device=raw_device,
            value=try_parse_int_float_str(value)
        ))
