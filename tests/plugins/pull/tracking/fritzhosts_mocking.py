"""FritzBox mocking."""


class FritzBoxHostsMock:  # pragma: no cover
    """Mocks the fritzconnection.FritzHosts class."""
    def __init__(self):
        self.address = None
        self.user = None
        self.password = None
        self.calls = 0

    def __call__(self, address, user, password):
        """The actual instantiation of mock from a client perspective."""
        self.address = address
        self.user = user
        self.password = password
        return self

    @property
    def modelname(self):
        """Return the name of the fritzbox model / make."""
        return "Fritz!Box Mock v1.0"

    def get_hosts_info(self):
        """Return the known hosts."""
        _ = self  # Fake usage
        self.calls += 1
        return [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:13", 'ip': '192.168.178.11', 'name': 'pc2', 'status': False},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3',
             'status': self.calls <= 1}
        ]

    def get_specific_host_entry(self, mac_address):
        """Return the host associated to the given mac address."""
        if mac_address == '12:34:56:78:14':
            self.calls += 1
        _map = {
            '12:34:56:78:12': {
                'NewIPAddress': '192.168.178.10', 'NewActive': True, 'NewHostName': 'pc1'
            },
            '12:34:56:78:13': {
                'NewIPAddress': '192.168.178.11', 'NewActive': False, 'NewHostName': 'pc2'
            },
            '12:34:56:78:14': {
                'NewIPAddress': '192.168.178.12', 'NewActive': self.calls <= 1, 'NewHostName': 'pc3'
            }
        }
        return _map[mac_address]
