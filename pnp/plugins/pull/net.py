"""Network related plugins."""

import socket
import ssl
from datetime import datetime, timedelta
from typing import Tuple

from glom import glom

from pnp.plugins import load_optional_module
from pnp.plugins.pull import Polling
from pnp.typing import Payload
from pnp.utils import is_local, bps_mbps


class PortProbe(Polling):
    """
    Periodically establishes socket connection to check if anybody is listening
    on a given server on a specific port.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/net.PortProbe/index.md
    """

    CONST_SERVER = 'server'
    CONST_PORT = 'port'
    CONST_REACHABLE = 'reachable'

    def __init__(self, port, server='localhost', timeout=1, **kwargs):
        super().__init__(**kwargs)
        self.port = int(port)
        self.server = str(server)
        self.timeout = int(timeout)

    def poll(self):
        if is_local(self.server):
            available = self._local_probe()
        else:
            available = self._remote_probe()

        return {
            self.CONST_SERVER: self.server,
            self.CONST_PORT: self.port,
            self.CONST_REACHABLE: available
        }

    def _remote_probe(self):
        """Will open a socket connection and try to connect to the specified port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.server, self.port))
            try:
                # This might fail if the socket couldn't connect
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            return result == 0

    def _local_probe(self):
        """Will try to run a socket server listening on the specified port. This is a
        much better approach compared to try to connect to a server. Connecting to the
        server might flood logs, trigger actions, ..."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('127.0.0.1', self.port))
                sock.listen(0)
            with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
                sock.bind(('::1', self.port))
                sock.listen(0)
            return False
        except socket.error:
            return True


class Speedtest(Polling):
    """
    Periodically tests your real internet download / upload speed as well as the ping latency.
    """

    EXTRA = 'speedtest'

    OUTPUT_SPEC = {
        'download_speed_bps': 'download',  # in Bits/s
        'download_speed_mbps': ('download', bps_mbps),  # in Megabits/s
        'upload_speed_bps': 'upload',  # in Bits/s
        'upload_speed_mbps': ('upload', bps_mbps),  # in Bits/s
        'ping_latency': 'ping',  # in ms
        'result_image': 'share',  # Image provided by speedtest.net to share
        'server': {
            'name': 'server.sponsor',  # The sponsor of the host
            'host': 'server.host',  # The host name
            'location': {
                'city': 'server.name',
                'country': 'server.country',
                'lat': 'server.lat',
                'lon': 'server.lon'
            }
        },
        'client': {
            'isp': 'client.isp',  # Your Internet service provider
            'rating': 'client.isprating'  # The rating of your isp
        }
    }

    def poll(self) -> Payload:
        speedtest = load_optional_module('speedtest', self.EXTRA)

        client = speedtest.Speedtest()
        client.get_servers()
        client.get_best_server()
        client.download(threads=None)
        client.upload(threads=None)
        client.results.share()

        res = client.results.dict()
        return glom(res, self.OUTPUT_SPEC)


class SSLVerify(Polling):
    """
    Periodically checks if the ssl certificate of a given host is valid and how
    many days are remaining before the certificate will expire.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/net.SSLVerify/index.md
    """

    def __init__(self, host: str, timeout: float = 3.0, **kwargs):
        super().__init__(**kwargs)
        self.host = str(host)
        self.timeout = float(timeout)

    def _ssl_expiry_datetime(self) -> Tuple[datetime, timedelta]:
        """
        Fetches the expiration date of the ssl certificate.

        Returns:
            Tuple that contains the timestamp the certificate will expire
            and the number of days left.
        """
        ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=self.host,
        )
        conn.settimeout(self.timeout)

        conn.connect((self.host, 443))
        self.logger.debug("SSL Host: %s", self.host)
        ssl_info = conn.getpeercert()
        self.logger.debug("Connection to host %s successful", self.host)

        # parse the string from the certificate into a Python datetime object
        expires = datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
        self.logger.debug('SSL certificate for %s expires at %s', self.host, expires.isoformat())

        return expires, expires - datetime.utcnow()

    def poll(self) -> Payload:
        expires_at, expires_delta = self._ssl_expiry_datetime()
        return {
            'host': self.host,
            'payload': {
                'expires_days': expires_delta.days,
                'expires_at': expires_at,
                'expired': expires_delta <= timedelta(days=0)
            }
        }
