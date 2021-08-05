"""Pull: net.SSLVerify."""

import socket
import ssl
from datetime import datetime, timedelta
from typing import Tuple, Any

from pnp.plugins.pull import SyncPolling
from pnp.typing import Payload


class SSLVerify(SyncPolling):
    """
    Periodically checks if the ssl certificate of a given host is valid and how
    many days are remaining before the certificate will expire.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#net-sslverify
    """
    __REPR_FIELDS__ = ['host', 'timeout']

    def __init__(self, host: str, timeout: float = 3.0, **kwargs: Any):
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
        expires = datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)  # type: ignore
        self.logger.debug('SSL certificate for %s expires at %s', self.host, expires.isoformat())

        return expires, expires - datetime.utcnow()

    def _poll(self) -> Payload:
        expires_at, expires_delta = self._ssl_expiry_datetime()
        return {
            'host': self.host,
            'payload': {
                'expires_days': expires_delta.days,
                'expires_at': expires_at,
                'expired': expires_delta <= timedelta(days=0)
            }
        }
