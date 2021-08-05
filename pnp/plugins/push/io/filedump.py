"""Push: io.FileDump"""
import os
import time
from typing import Optional, Any

from pnp import validator
from pnp.plugins.push import SyncPush
from pnp.plugins.push.envelope import Envelope
from pnp.typing import Payload


class FileDump(SyncPush):
    """
    This push dumps the given `payload` to a file to the specified `directory`.
    If argument `file_name` is None, a name will be generated based on the current datetime
    (%Y%m%d-%H%M%S).
    If `file_name` is not passed (or None) you should pass `extension` to specify the extension of
    the generated file name.
    Argument `binary_mode` controls whether the dump is binary (mode=wb) or text (mode=w).


    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#io-filedump
    """

    __REPR_FIELDS__ = ['binary_mode', 'directory', 'extension', 'file_name']

    def __init__(
            self, directory: Optional[str] = None, file_name: Optional[str] = None,
            extension: str = '.dump', binary_mode: bool = True,
            **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.directory = directory or self.base_path
        validator.is_directory(directory=self.directory)
        self.extension = self._parse_extension(extension)
        self.binary_mode = bool(binary_mode)
        self.file_name = self._parse_file_name(file_name)

    @staticmethod
    def _parse_file_name(value: Any) -> Optional[str]:
        return value and str(value)

    @staticmethod
    def _parse_extension(value: Any) -> str:
        value_str = str(value)
        if not value_str.startswith('.'):
            return '.' + value_str
        return value_str

    @Envelope.unwrap
    @Envelope.parse('file_name')
    @Envelope.parse('extension')
    @Envelope.drop
    def _push_unwrap(self, file_name: Optional[str], extension: str, payload: Payload) -> str:
        if file_name is None:
            file_name = time.strftime("%Y%m%d-%H%M%S")
        file_path = os.path.join(self.directory, file_name + extension)
        with open(file_path, 'wb' if self.binary_mode else 'w') as fhandle:
            fhandle.write(str(payload) if not self.binary_mode else payload)

        return file_path

    def _push(self, payload: Payload) -> Payload:
        return self._push_unwrap(payload)  # pylint: disable=no-value-for-parameter
