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

    When the push is performed it returns the name of the created file.

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
        self.extension = str(extension)
        if not self.extension.startswith('.'):
            self.extension = '.' + self.extension
        self.binary_mode = bool(binary_mode)
        self.file_name = Validator.cast_or_none(str, file_name)

    def _generate_file_name(self):
        return os.path.join(self.directory, time.strftime("%Y%m%d-%H%M%S") + self.extension)

    def push(self, payload):
        file_name = self.file_name
        if file_name is None:
            file_name = self._generate_file_name()
        with open(file_name, 'wb' if self.binary_mode else 'w') as fs:
            fs.write(str(payload) if not self.binary_mode else payload)

        return file_name
