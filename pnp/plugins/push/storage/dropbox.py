"""Push: storage.Dropbox."""
import urllib.parse
from typing import Optional, Any

from dropbox import dropbox
from typeguard import typechecked

from pnp.plugins.push import SyncPush
from pnp.plugins.push.envelope import Envelope
from pnp.typing import Payload
from pnp.utils import get_bytes

__EXTRA__ = 'dropbox'


class Dropbox(SyncPush):
    """
    Uploads provided file to the specified dropbox account.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#storage-dropbox
    """
    __REPR_FIELDS__ = ['create_shared_link', 'target_file_name']

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
    def _make_raw_file_url(shared_url: str) -> str:
        url_parts = list(urllib.parse.urlparse(shared_url))
        # Replace all query params with ?raw=1
        url_parts[4] = urllib.parse.urlencode({'raw': '1'})
        return str(urllib.parse.urlunparse(url_parts))

    @Envelope.unwrap
    @Envelope.parse('target_file_name')
    @Envelope.drop
    def _push_unwrap(self, target_file_name: str, payload: Payload) -> Payload:
        target_file_name = self._sanitze_target_file_name(target_file_name)

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

    def _push(self, payload: Payload) -> Payload:
        return self._push_unwrap(payload)    # pylint: disable=no-value-for-parameter
