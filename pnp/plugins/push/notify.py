"""Notification related push plugins."""

from . import PushBase, enveloped
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

    @enveloped
    def push(self, envelope, payload):  # pylint: disable=arguments-differ
        pbullet, urlparse = self._load_deps()
        client = pbullet.Pushbullet(self.api_key)
        urlprofile = urlparse.urlparse(payload)
        self.logger.info("Sending message '%s' to Pushbullet", payload)
        if urlprofile.scheme and urlprofile.netloc:
            # Is URL
            self.logger.debug("Payload '%s' is an url", payload)
            mtype = self._guess_mimetype(payload)
            if not mtype:
                # Some link
                self.logger.debug(
                    "Payload '%s' has no mimetype associated", payload
                )
                client.push_link(self.title, payload)
            else:
                # Some file
                self.logger.debug(
                    "Guessed type '%s' for payload '%s'", mtype, payload
                )
                client.push_file(
                    file_name=self._safe_basename(urlprofile.path),
                    file_type=mtype,
                    file_url=payload,
                    title=self.title
                )
        else:
            # Is NOT url
            self.logger.debug("Payload '%s' is a simple note", payload)
            client.push_note(self.title, payload)

        return {'data': payload, **envelope} if envelope else payload
