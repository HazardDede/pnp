from . import PushBase
from .. import load_optional_module
from ...utils import auto_str_ignore, get_bytes
from ...validator import Validator


@auto_str_ignore(['api_key'])
class Dropbox (PushBase):
    __prefix__ = 'dropbox'

    EXTRA = 'dropbox'

    def __init__(self, api_key, target_file_name=None, create_shared_link=True, **kwargs):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.target_file_name = str(target_file_name)
        self.create_shared_link = bool(create_shared_link)

    @staticmethod
    def _sanitze_target_file_name(val):
        Validator.is_not_none(val=val)
        val = str(val)
        if not val.startswith('/'):
            return '/' + val
        return val

    @staticmethod
    def _make_raw_file_url(shared_url):
        try:
            import urlparse
            from urllib import urlencode
        except:  # For Python 3
            import urllib.parse as urlparse
            from urllib.parse import urlencode

        url_parts = list(urlparse.urlparse(shared_url))
        # Replace all query params with ?raw=1
        url_parts[4] = urlencode({'raw': '1'})
        return urlparse.urlunparse(url_parts)

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)
        # Override target_file_name via envelope
        target_file_name = self._sanitze_target_file_name(self._parse_envelope_value('target_file_name', envelope))

        # Upload file or stream to dropbox
        dropbox = load_optional_module('dropbox', self.EXTRA)
        dbx = dropbox.Dropbox(self.api_key)
        fcontent = get_bytes(real_payload)  # Might be a file or a stream
        self.logger.info("[{self.name}] Uploading file to dropbox '{target_file_name}'".format(**locals()))
        metadata = dbx.files_upload(fcontent, target_file_name, mode=dropbox.files.WriteMode("overwrite"))

        res = dict(
            name=metadata.name,
            id=metadata.id,
            content_hash=metadata.content_hash,
            size=metadata.size,
            path=metadata.path_display,
            shared_link=None,
            raw_link=None
        )
        if self.create_shared_link:
            # create a shared link
            shared_link = dbx.sharing_create_shared_link(target_file_name)
            res['shared_link'] = shared_link.url
            res['raw_link'] = self._make_raw_file_url(shared_link.url)

        return res
