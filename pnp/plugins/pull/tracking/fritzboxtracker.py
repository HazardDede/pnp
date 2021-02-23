"""Pull: tracking.FritzBoxTracker."""

from typing import Dict, Any, List, Optional

import fritzconnection.lib.fritzhosts as fritz_hosts

from pnp import validator
from pnp.plugins.pull import SyncPolling
from pnp.typing import Payload


__EXTRA__ = 'fritz'


CONST_IP_DEFAULT = '169.254.1.1'  # This IP should be valid for all FRITZ!Box routers.
CONST_USER_DEFAULT = 'admin'
CONST_PASSWORD_DEFAULT = ''


class FritzBoxTracker(SyncPolling):
    """
    Tracks connected / not connected devices using the Fritz!Box api.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#tracker-fritzboxtracker

    """

    __REPR_FIELDS__ = ['host', 'offline_delay', 'user', 'whitelist']

    def __init__(
            self,
            host: str = CONST_IP_DEFAULT, user: str = CONST_USER_DEFAULT,
            password: str = CONST_PASSWORD_DEFAULT, offline_delay: int = 0,
            whitelist: Optional[List[str]] = None, **kwargs: Any
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
        self._cache: Dict[str, int] = {}

    def _setup(self) -> None:
        if self.fritz_box:
            # Nothing to do
            return

        try:
            self.fritz_box = fritz_hosts.FritzHosts(
                address=self.host,
                user=self.user,
                password=self.password
            )
            assert self.fritz_box
            if not self.fritz_box.modelname:
                raise ValueError()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception(
                "Cannot connect to the Fritz!Box @ %s. Please review the configuration",
                self.host
            )
            self.fritz_box = None

        self.logger.info("Connected to the Fritz!Box @ %s", self.host)

    def _parse_host(self, host_entry: Dict[str, Any]) -> Dict[str, Any]:
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

    def _get_host_list(self) -> List[Dict[str, Any]]:
        if not self.fritz_box:
            raise RuntimeError("Fritz!Box was not properly initialized")

        if not self.whitelist:
            # Get all hosts
            return self.fritz_box.get_hosts_info()  # type: ignore

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

    def _poll(self) -> Payload:
        self._setup()
        if not self.fritz_box:
            return None  # No connection, no data

        return [
            self._adjust_status(self._parse_host(host))
            for host in self._get_host_list()
        ]
