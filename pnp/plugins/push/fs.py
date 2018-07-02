import os
import time

from . import PushBase
from ...validator import Validator


class FileDump(PushBase):
    """
    This push dumps the given `payload` to a file to the specified `directory`.
    If argument `file_name` is None, a name will be generated based on the current datetime (%Y%m%d-%H%M%S).
    If `file_name` is not passed (or None) you should pass `extension` to specify the extension of the generated
    file name.
    Argument `binary_mode` controls whether the dump is binary (mode=wb) or text (mode=w).

    Args:
        directory (str): The target directory to store the dumps.
        file_name (str or None): The name of the file to dump. If set to None a file name will be automatically
            generated. You can specify the file_name via the envelope, too.
            Envelope will override __init__ file name.
        extension (str): The extension to use when the file name is automatically generated. Can be overridden by
            envelope.
        binary_mode (bool): If set to True the file will be written in binary mode ('wb'); otherwise in text mode ('w').

    Returns:

        When the push is performed it returns the name of the created file.

    Example configuration:

        name: file_dump
        pull:
          plugin: pnp.plugins.pull.simple.Repeat
          args:
            repeat: "Hello World"
        push:
          plugin: pnp.plugins.push.fs.FileDump
          args:
            directory: "/tmp"
            file_name: null  # Auto-generated file (timestamp)
            extension: ".txt"  # Extension of auto-generated file
            binary_mode: False  # text mode

    Examples:

        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     # Automatic generated file name with extension '.dump'
        ...     dut = FileDump(name='doctest', directory=tmpdir, binary_mode=False)
        ...     created_file = dut.push("I am the content")  #  e.g. 20180616-123159.dump
        ...     with open(created_file, 'r') as fs:
        ...         assert fs.read() == "I am the content"

    """
    def __init__(self, directory='.', file_name=None, extension='.dump', binary_mode=True, **kwargs):
        super().__init__(**kwargs)
        self.directory = directory
        Validator.is_directory(directory=self.directory)
        self.extension = self._parse_extension(extension)
        self.binary_mode = bool(binary_mode)
        self.file_name = self._parse_file_name(file_name)

    def _parse_file_name(self, value):
        return Validator.cast_or_none(str, value)

    def _parse_extension(self, value):
        value = str(value)
        if not value.startswith('.'):
            return'.' + value
        return value

    def push(self, payload):
        envelope, payload = self.envelope_payload(payload)
        file_name = self._parse_envelope_value('file_name', envelope)
        extension = self._parse_envelope_value('extension', envelope)

        if file_name is None:
            file_name = time.strftime("%Y%m%d-%H%M%S")
        file_path = os.path.join(self.directory, file_name + extension)
        with open(file_path, 'wb' if self.binary_mode else 'w') as fs:
            fs.write(str(payload) if not self.binary_mode else payload)

        return file_path
