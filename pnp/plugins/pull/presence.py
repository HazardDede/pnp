"""Presence / Occupancy related plugins."""

from typing import Dict, Any, List, Optional

from pnp import validator
from pnp.plugins import load_optional_module
from pnp.plugins.pull import Polling
from pnp.typing import Payload


class FritzBoxTracker(Polling):
    """Tracks connected / not connected devices using the Fritz!Box api."""

    EXTRA = 'fritz'

    CONF_DEFAULT_IP = '169.254.1.1'  # This IP should be valid for all FRITZ!Box routers.
    CONF_DEFAULT_USER = 'admin'
    CONF_DEFAULT_PASSWORD = ''

    def __init__(
            self,
            host: str = CONF_DEFAULT_IP, user: str = CONF_DEFAULT_USER,
            password: str = CONF_DEFAULT_PASSWORD, offline_delay: int = 0,
            whitelist: Optional[List[str]] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.user = str(user)
        self.password = str(password)
        self.host = str(host)
        self.offline_delay = int(offline_delay)
        if self.offline_delay < 0:
            self.offline_delay = 0
        if whitelist:
            validator.is_iterable_but_no_str(whitelist=whitelist)
        self.whitelist = whitelist and [str(item) for item in whitelist]
        self.fritz_box = None
        self._cache = {}

    def _setup(self):
        if self.fritz_box:
            # Nothing to do
            return

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
        if 'NewIPAddress' in host_entry:  # Result structure from specific host call (whitelist)
            return {
                'mac': host_entry['mac'],
                'ip': host_entry['NewIPAddress'],
                'status': host_entry['NewActive'],
                'name': host_entry['NewHostName']
            }
        return host_entry

    def _adjust_status(self, device: Dict[str, Any]) -> Dict[str, Any]:
        mac, status = device['mac'], device['status']
        if status:  # Online, no adjustment
            self._cache[mac] = 0
            return device

        # Status = offline
        if mac not in self._cache:
            self._cache[mac] = self.offline_delay
            return device  # Never seen before -> no adjustment

        if self._cache[mac] < self.offline_delay:
            self._cache[mac] += 1
            device['status'] = True  # Fake online

        return device

    def _get_host_list(self):
        if not self.whitelist:
            return self.fritz_box.get_hosts_info()  # Get all hosts

        # Whitelist is used: Different call to fritzbox
        res = []
        for mac in self.whitelist:
            try:
                device = self.fritz_box.get_specific_host_entry(mac_address=str(mac))
                device['mac'] = str(mac)
                res.append(device)
            except KeyError:
                self.logger.warning("Fritz!Box does not know about the device '%s'", str(mac))

        return res

    def poll(self) -> Payload:
        self._setup()
        if not self.fritz_box:
            return None  # No connection, no data

        return [
            self._adjust_status(self._parse_host(host))
            for host in self._get_host_list()
        ]
