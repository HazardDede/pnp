"""Network related plugins."""

import socket

from . import Polling
from ...utils import is_local


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
