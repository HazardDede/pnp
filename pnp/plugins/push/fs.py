import os
import time

from . import PushBase
from ...validator import Validator


class FileDump(PushBase):
    def __init__(self, directory='.', extension='.dump', binary_mode=True, **kwargs):
        super().__init__(**kwargs)
        self.directory = directory
        Validator.is_directory(directory=self.directory)
        self.extension = str(extension)
        self.binary_mode = bool(binary_mode)

    def _generate_file_name(self):
        return os.path.join(self.directory, time.strftime("%Y%m%d-%H%M%S") + self.extension)

    def push(self, payload):
        file_name = self._generate_file_name()
        with open(file_name, 'wb' if self.binary_mode else 'w') as fs:
            fs.write(payload)

        return file_name
