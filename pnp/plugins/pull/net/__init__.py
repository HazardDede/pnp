"""Network related pulls."""

import sys

from pnp.plugins.pull import try_import_pull

__IMPORTS__ = [
    ('net.ftpserver', 'FTPServer'),
    ('net.portprobe', 'PortProbe'),
    ('net.speedtest', 'Speedtest'),
    ('net.sslverify', 'SSLVerify')
]

thismodule = sys.modules[__name__]
for import_path, clazz in __IMPORTS__:
    module = try_import_pull(import_path, clazz)
    setattr(thismodule, clazz, module)

__all__ = [clazz for _, clazz in __IMPORTS__]
