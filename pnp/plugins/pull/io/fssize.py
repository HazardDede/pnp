"""Pull: io.FSSize"""

import os
from typing import Any, Dict, Iterable, Union, Optional

from pnp.plugins import PluginStoppedError
from pnp.plugins.pull import SyncPolling
from pnp.typing import Payload
from pnp.utils import make_list


PathLike = str
PathDict = Dict[str, PathLike]  # Alias of path -> actual path
PathList = Iterable[PathLike]  # List of path items
PathDef = Union[PathDict, PathList, PathLike]


class FSSize(SyncPolling):
    """
    Periodically determines the size of the specified files or directories in bytes.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#io-fssize
    """

    __REPR_FIELDS__ = ['fail_on_error', 'paths']

    def __init__(self, paths: PathDef, fail_on_error: bool = True, **kwargs: Any):
        super().__init__(**kwargs)
        self.paths: PathDict
        if isinstance(paths, dict):
            self.paths = paths  # alias -> file path mapping
        else:
            # No explicit alias: Use the basename of the file or directory
            self.paths = {os.path.basename(str(fp)): str(fp) for fp in make_list(paths) or []}
        self.fail_on_error = bool(fail_on_error)

    @staticmethod
    def _file_size(path: PathLike) -> int:
        return os.path.getsize(path)

    def _dir_size(self, path: PathLike) -> int:
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for fname in filenames:
                fp = os.path.join(dirpath, fname)
                try:
                    total_size += self._file_size(os.path.realpath(fp))
                except FileNotFoundError:
                    self.logger.warning(
                        "File %s does not exists when calculating the directory size", fp)
                finally:
                    if self.stopped:
                        raise PluginStoppedError(
                            "Aborted calculation of directory size, due to stop of plugin")

        return total_size

    def _size(self, path: PathLike) -> Optional[int]:
        try:
            if os.path.isdir(path):
                return self._dir_size(path)
            return self._file_size(path)
        except (FileNotFoundError, NotADirectoryError):
            if self.fail_on_error:
                raise
            return None

    def _poll(self) -> Payload:
        return {
            alias: self._size(fp)
            for alias, fp in self.paths.items()
        }
