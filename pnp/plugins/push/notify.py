"""Notification related push plugins."""

from . import PushBase
from .. import load_optional_module
from ...utils import auto_str_ignore


@auto_str_ignore(['api_key'])
class Pushbullet(PushBase):
    """
    Sends a message to the Pushbullet service. The type of the message will guessed:

    - `push_link` for a single http link
    - `push_file` if the link is directed to a file (mimetype will be guessed)
    - `push_note` for everything else (converted to str)

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/notify.Pushbullet/index.md
    """
    __prefix__ = 'pushbullet'

    EXTRA = 'pushbullet'

    def __init__(self, api_key, title='pnp', **kwargs):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.title = str(title)

    def _load_deps(self):
        pbullet = load_optional_module('pushbullet', self.EXTRA)
        try:
            import urlparse
        except:  # For Python 3, pylint: disable=bare-except
            import urllib.parse as urlparse

        return pbullet, urlparse

    def _guess_mimetype(self, url):
        import mimetypes
        _, urlparse = self._load_deps()
        res = urlparse.urlparse(url)
        if not res.path:
            return None
        mtype, _ = mimetypes.guess_type(res.path)
        return mtype

    @staticmethod
    def _safe_basename(name):
        import os
        try:
            return os.path.basename(name)
        except:  # pylint: disable=bare-except
            return name

    def push(self, payload):
        _, real_payload = self.envelope_payload(payload)

        pbullet, urlparse = self._load_deps()
        client = pbullet.Pushbullet(self.api_key)
        urlprofile = urlparse.urlparse(real_payload)
        self.logger.info("[%s] Sending message '%s' to Pushbullet", self.name, real_payload)
        if urlprofile.scheme and urlprofile.netloc:
            # Is URL
            self.logger.debug("[%s] Payload '%s' is an url", self.name, real_payload)
            mtype = self._guess_mimetype(real_payload)
            if not mtype:
                # Some link
                self.logger.debug(
                    "[%s] Payload '%s' has no mimetype associated", self.name, real_payload
                )
                client.push_link(self.title, real_payload)
            else:
                # Some file
                self.logger.debug(
                    "[%s] Guessed type '%s' for payload '%s'", self.name, mtype, real_payload
                )
                client.push_file(
                    file_name=self._safe_basename(urlprofile.path),
                    file_type=mtype,
                    file_url=real_payload,
                    title=self.title
                )
        else:
            # Is NOT url
            self.logger.debug("[%s] Payload '%s' is a simple note", self.name, real_payload)
            client.push_note(self.title, real_payload)

        return payload
