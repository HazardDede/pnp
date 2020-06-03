"""Contains file system related push plugins."""

import os
import time

from pnp import validator
from pnp.plugins.push import PushBase, enveloped, parse_envelope, drop_envelope


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
        validator.is_directory(directory=self.directory)
        self.extension = self._parse_extension(extension)
        self.binary_mode = bool(binary_mode)
        self.file_name = self._parse_file_name(file_name)

    @staticmethod
    def _parse_file_name(value):
        return value and str(value)

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


class Zipper(PushBase):
    """
    Zips the given source directory or file and returns the path to the created zip
    archive.

    Args:
        source (str): Specifies the source directory or file to zip. If not passed the
            source can be specified by the envelope at runtime.
        out_path (str): Specifies the path to the general output path where all target
            zip files should be generated. If not passed the systems temp directory is
            used.

    Returns:
        Returns the absolute path to the created zip file.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/fs.Zipper/index.md

    """

    def __init__(self, source=None, out_path=None, **kwargs):
        super().__init__(**kwargs)
        self.source = self._parse_source(source)
        self.out_path = self._parse_out_path(out_path)

    @staticmethod
    def _parse_source(value):
        if not value:
            return None
        value = str(value)
        if not os.path.isfile(value) and not os.path.isdir(value):
            raise ValueError("Argument 'source' is neither a directory nor a file")
        return value

    @staticmethod
    def _parse_out_path(value):
        if not value:
            import tempfile
            return tempfile.gettempdir()
        validator.is_directory(out_path=value)
        return os.path.abspath(str(value))

    @enveloped
    @drop_envelope
    def push(self, payload):
        source = self._parse_source(self.source or payload)

        if os.path.isdir(source):
            # Directory branch
            from ...shared.zipping import zipdir, zipignore
            base_dir_name = os.path.basename(os.path.normpath(source))
            out_file = os.path.join(self.out_path, base_dir_name + '.zip')
            ignore_list = zipignore(source)
            zipdir(source, out_file, ignore_list)
            return out_file

        # File branch
        from ...shared.zipping import zipfiles
        out_file = os.path.join(self.out_path, os.path.basename(source) + '.zip')
        zipfiles(source, out_file)
        return out_file
