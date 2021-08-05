"""Push: io.Zipper."""

import os
from typing import Optional, Any

from pnp import validator
from pnp.plugins.push import SyncPush, PushExecutionError
from pnp.plugins.push.envelope import Envelope
from pnp.shared.zipping import zipfiles, zipdir, zipignore
from pnp.typing import Payload


class Zipper(SyncPush):
    """
    Zips the given source directory or file and returns the path to the created zip
    archive.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#io-zipper

    """
    __REPR_FIELDS__ = ['archive_name', 'out_path', 'source']

    def __init__(
            self, source: Optional[str] = None, out_path: Optional[str] = None,
            archive_name: Optional[str] = None, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.source = self._parse_source(source)
        self.out_path = self._parse_out_path(out_path)
        self.archive_name = self._parse_archive_name(archive_name)

    @staticmethod
    def _parse_source(value: Any) -> Optional[str]:
        if not value:
            return None
        value_str = str(value)
        if not os.path.isfile(value_str) and not os.path.isdir(value_str):
            raise ValueError("Argument 'source' is neither a directory nor a file")
        return value_str

    @staticmethod
    def _parse_out_path(value: Any) -> str:
        if not value:
            import tempfile
            return tempfile.gettempdir()
        validator.is_directory(out_path=value)
        return os.path.abspath(str(value))

    @staticmethod
    def _parse_archive_name(value: Any) -> Optional[str]:
        return value and str(value)

    @Envelope.unwrap
    @Envelope.parse('source')
    @Envelope.parse('archive_name')
    @Envelope.drop
    def _push_unwrap(
            self, archive_name: Optional[str], source: Optional[str], payload: Payload
    ) -> str:
        source = self._parse_source(source or self.source or payload)

        if not source:
            raise PushExecutionError("Attribute source is empty or None")

        if os.path.isdir(source):
            # Directory branch
            base_dir_name = os.path.basename(os.path.normpath(source))
            out_file = (
                os.path.join(self.out_path, archive_name) if archive_name else
                os.path.join(self.out_path, base_dir_name + '.zip')
            )
            ignore_list = zipignore(source)
            zipdir(source, out_file, ignore_list)
            return out_file

        if os.path.isfile(source):
            # File branch
            out_file = (
                os.path.join(self.out_path, archive_name) if archive_name else
                os.path.join(self.out_path, os.path.basename(source) + '.zip')
            )
            zipfiles(source, out_file)
            return out_file

        raise PushExecutionError(f"Source '{source}' is neither a valid directory nor a valid file")

    def _push(self, payload: Payload) -> Payload:
        return self._push_unwrap(payload)  # pylint: disable=no-value-for-parameter
