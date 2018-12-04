from . import PushBase
from .. import load_optional_module
from ...utils import auto_str_ignore


@auto_str_ignore(['api_key'])
class Pushbullet (PushBase):
    __prefix__ = 'pushbullet'

    EXTRA = 'pushbullet'

    def __init__(self, api_key, title='pnp', **kwargs):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.title = str(title)

    def _load_deps(self):
        pb = load_optional_module('pushbullet', self.EXTRA)
        try:
            import urlparse
        except:  # For Python 3
            import urllib.parse as urlparse

        return pb, urlparse

    def _guess_mimetype(self, url):
        import mimetypes
        _, up = self._load_deps()
        res = up.urlparse(url)
        if not res.path:
            return None
        mt, _ = mimetypes.guess_type(res.path)
        return mt

    def _safe_basename(self, name):
        import os
        try:
            return os.path.basename(name)
        except:
            return name

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)

        pb, up = self._load_deps()
        client = pb.Pushbullet(self.api_key)
        pr = up.urlparse(real_payload)
        self.logger.info("[{self.name}] Sending message '{real_payload}' to Pushbullet".format(**locals()))
        if pr.scheme and pr.netloc:
            # Is URL
            self.logger.debug("[{self.name}] Payload '{real_payload}' is an url".format(**locals()))
            mt = self._guess_mimetype(real_payload)
            if not mt:
                # Some link
                self.logger.debug("[{self.name}] Payload '{real_payload}' has no mimetype associated"
                                  .format(**locals()))
                client.push_link(self.title, real_payload)
            else:
                # Some file
                self.logger.debug("[{self.name}] Guessed type '{mt}' for payload '{real_payload}'".format(**locals()))
                client.push_file(
                    file_name=self._safe_basename(pr.path),
                    file_type=mt,
                    file_url=real_payload,
                    title=self.title
                )
        else:
            # Is NOT url
            self.logger.debug("[{self.name}] Payload '{real_payload}' is a simple note".format(**locals()))
            client.push_note(self.title, real_payload)

        return payload
