"""Storage related pushes."""

import sys

from pnp.plugins.push import try_import_push

__IMPORTS__ = [
    ('storage.dropbox', 'Dropbox'),
]

thismodule = sys.modules[__name__]
for import_path, clazz in __IMPORTS__:
    module = try_import_push(import_path, clazz)
    setattr(thismodule, clazz, module)

__all__ = [clazz for _, clazz in __IMPORTS__]
