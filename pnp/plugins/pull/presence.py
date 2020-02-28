"""Presence / Occupancy related plugins."""
from typing import Dict, Any

from . import Polling
from .. import load_optional_module
from ...typing import Payload


class FritzBoxTracker(Polling):
    """Tracks connected / not connected devices using the Fritz!Box api."""

    EXTRA = 'fritz'

    CONF_DEFAULT_IP = '169.254.1.1'  # This IP should be valid for all FRITZ!Box routers.
    CONF_DEFAULT_USER = 'admin'
    CONF_DEFAULT_PASSWORD = ''

    def __init__(
            self,
            host: str = CONF_DEFAULT_IP, user: str = CONF_DEFAULT_USER,
            password: str = CONF_DEFAULT_PASSWORD, **kwargs
    ):
        super().__init__(**kwargs)
        self.user = str(user)
        self.password = str(password)
        self.host = str(host)
        self.fritz_box = None

    def _setup(self):
        if not self.fritz_box:
            fritz_hosts = load_optional_module('fritzconnection.lib.fritzhosts', self.EXTRA)
            try:
                self.fritz_box = fritz_hosts.FritzHosts(
                    address=self.host,
                    user=self.user,
                    password=self.password
                )
                if not self.fritz_box.modelname:
                    raise ValueError()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception(
                    "Cannot connect to the Fritz!Box @ %s. Please review the configuration",
                    self.host
                )
                self.fritz_box = None

            self.logger.info("Connected to the Fritz!Box @ %s", self.host)

    def _parse_host(self, host_entry: Dict[str, Any]):
        _ = self  # Fake usage
        return host_entry

    def poll(self) -> Payload:
        self._setup()
        if not self.fritz_box:
            return None  # No connection, no data

        return [self._parse_host(host) for host in self.fritz_box.get_hosts_info()]
