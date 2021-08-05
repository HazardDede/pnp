"""Contains base stuff for user-defined functions in selector expressions."""

from abc import abstractmethod
from typing import Optional, Any, Union, Type

import cachetools

from pnp.plugins import Plugin, BrokenImport, InstallOptionalExtraError, try_import_plugin
from pnp.typing import (
    DurationLiteral
)
from pnp.utils import (
    parse_duration_literal,
    make_hashable
)


class UserDefinedFunction(Plugin):
    """Base class for a user defined expression."""

    __REPR_FIELDS__ = ['throttle']

    MAX_CACHE_SIZE = 12

    def __init__(self, throttle: Optional[DurationLiteral] = None, **kwargs: Any):
        """
        Initializer.

        Args:
            throttle: If set to a valid duration literal (e.g. 5m) the return value of the
              called functions will be cached for the given amount of time.
        """
        super().__init__(**kwargs)
        self.throttle = throttle and parse_duration_literal(throttle)
        self._cache = None
        if self.throttle:
            self._cache = cachetools.TTLCache(self.MAX_CACHE_SIZE, ttl=self.throttle)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._cache is None:
            return self.action(*args, **kwargs)

        hashable_args = (make_hashable(args), make_hashable(kwargs))
        try:
            return self._cache[hashable_args]
        except KeyError:
            res = self.action(*args, **kwargs)
            self._cache[hashable_args] = res
            return res

    @abstractmethod
    def action(self, *args: Any, **kwargs: Any) -> Any:
        """Actual definition of the hard-work of the user defined function."""
        raise NotImplementedError()


class BrokenImportUdf(UserDefinedFunction):
    """A UDF-class that represents a failed plugin load due to importing
    issues or other reasons.."""

    __REPR_FIELDS__ = ["extra", "error"]

    def __init__(self, extra: Optional[str], error: ImportError, **kwargs: Any):
        super().__init__(**kwargs)
        self.extra = extra
        self.error = error

    def _raise_error(self) -> None:
        if self.extra:
            raise InstallOptionalExtraError(self.extra) from self.error
        raise ImportError("Something went wrong when importing the plugin") from self.error

    def action(self, *args: Any, **kwargs: Any) -> Any:
        self._raise_error()


def try_import_udf(import_path: str, clazz: str) -> Union[BrokenImport, Type[UserDefinedFunction]]:
    """Tries to import a pull plugin located in given relative import_path
    and named after clazz."""
    udf = try_import_plugin("udf." + import_path, clazz, BrokenImportUdf)
    assert isinstance(udf, BrokenImport) or issubclass(udf, UserDefinedFunction)
    return udf
