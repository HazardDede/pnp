"""UDF: simple.Memory."""

from typing import Any

from pnp.plugins.udf import UserDefinedFunction


class Memory(UserDefinedFunction):
    """
    Returns a previously memorized value when called.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-memory

    Example:

        >>> dut = Memory(name='doctest', init='foo')
        >>> dut(), dut(new_memory='baz'), dut()
        ('foo', 'foo', 'baz')
        >>> cnt = Memory(name="doctest", init=1)
        >>> cnt(cnt.current + 1), cnt(cnt.current + 1), cnt(cnt.current + 1)
        (1, 2, 3)
    """
    __REPR_FIELDS__ = ['current']

    _MISSING = object()

    def __init__(self, init: Any = _MISSING, **kwargs: Any):
        super().__init__(**kwargs)
        self.current = init

    def _action(self, new_memory: Any = _MISSING) -> Any:
        try:
            if self.current is self._MISSING:
                return None if new_memory is self._MISSING else new_memory

            return self.current
        finally:
            if new_memory is not self._MISSING:
                self.current = new_memory

    def action(self, *args: Any, **kwargs: Any) -> Any:
        return self._action(*args, **kwargs)
