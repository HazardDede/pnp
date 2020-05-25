"""Storage related push plugins."""
from typing import Optional, Any

from typeguard import typechecked

from pnp.plugins import load_optional_module
from pnp.plugins.push import PushBase, enveloped, parse_envelope, drop_envelope
from pnp.utils import auto_str_ignore, get_bytes


@auto_str_ignore(['api_key'])
class Dropbox(PushBase):
    """
    Uploads provided file to the specified dropbox account.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/storage.Dropbox/index.md
    """
    EXTRA = 'dropbox'

    def __init__(
        self, api_key: str, target_file_name: Optional[str] = None,
        create_shared_link: bool = True, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.api_key = str(api_key)
        self.target_file_name = target_file_name and str(target_file_name)
        self.create_shared_link = bool(create_shared_link)

    @staticmethod
    @typechecked
    def _sanitze_target_file_name(val: str) -> str:
        if not val.startswith('/'):
            return '/' + val
        return val

    @staticmethod
    def _make_raw_file_url(shared_url):
        try:
            import urlparse
            from urllib import urlencode
        except ImportError:  # For Python 3
            import urllib.parse as urlparse
            from urllib.parse import urlencode

        url_parts = list(urlparse.urlparse(shared_url))
        # Replace all query params with ?raw=1
        url_parts[4] = urlencode({'raw': '1'})
        return urlparse.urlunparse(url_parts)

    @enveloped
    @parse_envelope('target_file_name')
    @drop_envelope
    def push(self, target_file_name, payload):  # pylint: disable=arguments-differ
        target_file_name = self._sanitze_target_file_name(target_file_name)

        # Upload file or stream to dropbox
        dropbox = load_optional_module('dropbox', self.EXTRA)
        dbx = dropbox.Dropbox(self.api_key, timeout=None)
        fcontent = get_bytes(payload)  # Might be a file or a stream
        self.logger.info("Uploading file to dropbox '%s'", target_file_name)
        metadata = dbx.files_upload(
            fcontent,
            target_file_name,
            mode=dropbox.files.WriteMode("overwrite")
        )

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
