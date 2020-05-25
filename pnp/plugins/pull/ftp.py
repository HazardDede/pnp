"""FTP related pulls."""

import copy
import tempfile
from contextlib import contextmanager

from pnp import validator
from pnp.plugins import load_optional_module
from pnp.plugins.pull import PullBase
from pnp.utils import is_iterable_but_no_str, make_list


class Server(PullBase):
    """
    Runs a ftp server on the specified port to receive and send files by ftp protocol.
    Optionally sets up a simple user/password authentication mechanism.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/ftp.Server/index.md
    """
    EXTRA = 'ftp'

    EVENT_CONNECT = 'connect'
    EVENT_DISCONNECT = 'disconnect'
    EVENT_FILE_RECEIVED = 'file_received'
    EVENT_FILE_RECEIVED_INCOMPLETE = 'file_received_incomplete'
    EVENT_FILE_SENT = 'file_sent'
    EVENT_FILE_SENT_INCOMPLETE = 'file_sent_incomplete'
    EVENT_LOGIN = 'login'
    EVENT_LOGOUT = 'logout'

    ALL_EVENTS = [EVENT_CONNECT, EVENT_DISCONNECT, EVENT_FILE_RECEIVED,
                  EVENT_FILE_RECEIVED_INCOMPLETE, EVENT_FILE_SENT, EVENT_FILE_SENT_INCOMPLETE,
                  EVENT_LOGIN, EVENT_LOGOUT]

    def __init__(self, directory=None, port=2121, user_pwd=None, events=None,
                 max_cons=256, max_cons_ip=5, **kwargs):
        super().__init__(**kwargs)
        self.port = int(port)
        self.max_cons = int(max_cons)
        self.max_cons_ip = int(max_cons_ip)
        validator.is_instance(str, allow_none=True, directory=directory)
        if directory:
            validator.is_directory(directory=directory)
        self.directory = directory
        if not user_pwd:  # No password -> anonymous access
            self.user = None
        elif isinstance(user_pwd, str):
            self.user = user_pwd
            self.password = ''
        elif is_iterable_but_no_str(user_pwd) and user_pwd:  # at least one element
            self.user = user_pwd[0]
            if len(user_pwd) > 1:  # Password too
                self.password = user_pwd[1]
        else:
            raise TypeError("Argument 'user_pwd' is expected to be a str (user) or a tuple of "
                            "user and password.")

        self.events = make_list(events) or copy.copy(self.ALL_EVENTS)
        if self.events:
            validator.subset_of(self.ALL_EVENTS, events=self.events)

        self.server = None

    def pull(self):
        with self._setup_directory() as ftp_directory:
            authorizer = self._setup_auth(ftp_directory)
            handler = self._setup_handler(authorizer)
            self.server = self._setup_server(handler)

            try:
                self.server.serve_forever()
            except OSError:
                # Bug on OSX when closing: [Errno 9] Bad file descriptor
                import traceback
                self.logger.warning("%s", traceback.format_exc())

    def stop(self):
        if self.server:
            self.server.close_all()
        return super().stop()

    @contextmanager
    def _setup_directory(self):
        if self.directory:
            yield self.directory
        else:
            with tempfile.TemporaryDirectory() as tmpdir:
                yield tmpdir

    def _setup_auth(self, ftp_directory):
        auth = load_optional_module('pyftpdlib.authorizers', self.EXTRA)
        authorizer = auth.DummyAuthorizer()
        if self.user:
            self.logger.debug(
                "Setting up authorization: %s:%s @ %s",
                self.user, '*' * len(self.password), ftp_directory
            )
            authorizer.add_user(self.user, self.password, ftp_directory, perm='elradfmw')
        else:
            self.logger.debug("Setting up anonymous access @ %s", ftp_directory)
            authorizer.add_anonymous(ftp_directory, perm='elradfmw')

        return authorizer

    def _setup_handler(self, authorizer):
        handlers = load_optional_module('pyftpdlib.handlers', self.EXTRA)
        handler = handlers.FTPHandler
        handler.authorizer = authorizer
        handler.banner = 'Welcome to pnp embedded ftp server'
        self._register_callbacks(handler)
        return handler

    def _setup_server(self, handler):
        self.logger.debug("Setting up server on 127.0.0.1:%s", str(self.port))
        servers = load_optional_module('pyftpdlib.servers', self.EXTRA)
        address = ('', self.port)
        server = servers.ThreadedFTPServer(address, handler)
        server.max_cons = self.max_cons
        server.max_cons_per_ip = self.max_cons_ip
        return server

    def _register_callbacks(self, handler):
        if self.EVENT_CONNECT in self.events:
            handler.on_connect = lambda that: \
                self.notify({'event': self.EVENT_CONNECT, 'data': {}})
        if self.EVENT_DISCONNECT in self.events:
            handler.on_disconnect = lambda that: \
                self.notify({'event': self.EVENT_DISCONNECT, 'data': {}})
        if self.EVENT_LOGIN in self.events:
            handler.on_login = lambda that, user: \
                self.notify({'event': self.EVENT_LOGIN, 'data': {'user': user}})
        if self.EVENT_LOGOUT in self.events:
            handler.on_logout = lambda that, user: \
                self.notify({'event': self.EVENT_LOGOUT, 'data': {'user': user}})
        if self.EVENT_FILE_SENT in self.events:
            handler.on_file_sent = lambda that, file_path: \
                self.notify({'event': self.EVENT_FILE_SENT, 'data': {'file_path': file_path}})
        if self.EVENT_FILE_RECEIVED in self.events:
            handler.on_file_received = lambda that, file_path: \
                self.notify({'event': self.EVENT_FILE_RECEIVED, 'data': {'file_path': file_path}})
        if self.EVENT_FILE_SENT_INCOMPLETE in self.events:
            handler.on_incomplete_file_sent = lambda that, file_path: \
                self.notify({
                    'event': self.EVENT_FILE_SENT_INCOMPLETE,
                    'data': {'file_path': file_path}
                })
        if self.EVENT_FILE_RECEIVED_INCOMPLETE in self.events:
            handler.on_incomplete_file_received = lambda that, file_path: \
                self.notify({
                    'event': self.EVENT_FILE_RECEIVED_INCOMPLETE,
                    'data': {'file_path': file_path}
                })
