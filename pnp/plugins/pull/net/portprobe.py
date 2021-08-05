"""Pull: net.PortProbe."""

import socket
from typing import Any

from pnp.plugins.pull import SyncPolling
from pnp.typing import Payload
from pnp.utils import is_local


CONST_SERVER = 'server'
CONST_PORT = 'port'
CONST_REACHABLE = 'reachable'


class PortProbe(SyncPolling):
    """
    Periodically establishes socket connection to check if anybody is listening
    on a given server on a specific port.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#net-portprobe
    """
    __REPR_FIELDS__ = ['port', 'server', 'timeout']

    def __init__(
            self, port: int, server: str = 'localhost', timeout: int = 1, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.port = int(port)
        self.server = str(server)
        self.timeout = int(timeout)

    def _poll(self) -> Payload:
        if is_local(self.server):
            available = self._local_probe()
        else:
            available = self._remote_probe()

        return {
            CONST_SERVER: self.server,
            CONST_PORT: self.port,
            CONST_REACHABLE: available
        }

    def _remote_probe(self) -> bool:
        """Will open a socket connection and try to connect to the specified port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.timeout)
            try:
                result = sock.connect_ex((self.server, self.port))
                # This might fail if the socket couldn't connect
                sock.shutdown(socket.SHUT_RDWR)
            except socket.gaierror:
                result = 1
            except OSError:
                pass
            return result == 0

    def _local_probe(self) -> bool:
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
