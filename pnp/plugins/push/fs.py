"""Contains file system related push plugins."""

import os
import time

from . import PushBase, enveloped, parse_envelope, drop_envelope
from ...validator import Validator


class FileDump(PushBase):
    """
    This push dumps the given `payload` to a file to the specified `directory`.
    If argument `file_name` is None, a name will be generated based on the current datetime
    (%Y%m%d-%H%M%S).
    If `file_name` is not passed (or None) you should pass `extension` to specify the extension of
    the generated file name.
    Argument `binary_mode` controls whether the dump is binary (mode=wb) or text (mode=w).


    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/fs.FileDump/index.md

    Examples:

        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     # Automatic generated file name with extension '.dump'
        ...     dut = FileDump(name='doctest', directory=tmpdir, binary_mode=False)
        ...     created_file = dut.push("I am the content")  #  e.g. 20180616-123159.dump
        ...     with open(created_file, 'r') as fs:
        ...         assert fs.read() == "I am the content"

    """
    def __init__(self, directory='.', file_name=None, extension='.dump', binary_mode=True,
                 **kwargs):
        super().__init__(**kwargs)
        self.directory = directory
        Validator.is_directory(directory=self.directory)
        self.extension = self._parse_extension(extension)
        self.binary_mode = bool(binary_mode)
        self.file_name = self._parse_file_name(file_name)

    @staticmethod
    def _parse_file_name(value):
        return Validator.cast_or_none(str, value)

    @staticmethod
    def _parse_extension(value):
        value = str(value)
        if not value.startswith('.'):
            return'.' + value
        return value

    @enveloped
    @parse_envelope('file_name')
    @parse_envelope('extension')
    @drop_envelope
    def push(self, file_name, extension, payload):  # pylint: disable=arguments-differ
        if file_name is None:
            file_name = time.strftime("%Y%m%d-%H%M%S")
        file_path = os.path.join(self.directory, file_name + extension)
        with open(file_path, 'wb' if self.binary_mode else 'w') as fhandle:
            fhandle.write(str(payload) if not self.binary_mode else payload)

        return file_path
