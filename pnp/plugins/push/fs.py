import base64

from . import PushBase


class FileLoad(PushBase):
    """
    """

    def __init__(self, binary_mode=True, base64=False, **kwargs):
        super().__init__(**kwargs)
        self.binary_mode = base64 or binary_mode
        self.base64 = base64

    def push(self, payload):
        load_file = None
        # filepath as a string argument
        if isinstance(payload, str):
            load_file = payload
        # compatibility with FileSystemWatcher
        elif isinstance(payload, dict):
            load_file = payload.get('destination', None) or payload.get('source', None)
        if load_file is None:
            raise ValueError("Couldn't extract any file name to load")

        self.logger.info("[{self.name}] Loading file '{load_file}'".format(**locals()))
        with open(load_file, 'rb' if self.binary_mode else 'r') as fs:
            return base64.b64encode(fs.read()) if self.base64 else fs.read()
