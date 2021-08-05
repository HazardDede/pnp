"""UDF: simple.Counter."""

from typing import Any

from pnp.plugins.udf import UserDefinedFunction


class Counter(UserDefinedFunction):
    """
    Memories a counter value which is increased everytime you call the udf.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-counter

    Example:

        >>> dut = Counter(name='doctest')
        >>> dut(), dut(), dut()
        (0, 1, 2)
        >>> dut = Counter(init=5, name='doctest')
        >>> dut(), dut(), dut()
        (5, 6, 7)
        >>> dut = Counter(init=-5, name='doctest')
        >>> dut(), dut(), dut()
        (0, 1, 2)
        >>> dut = Counter(init="5", name='doctest')
        >>> dut(), dut(), dut()
        (5, 6, 7)
    """
    __REPR_FIELDS__ = ['cnt']

    def __init__(self, init: int = 0, **kwargs: Any):
        super().__init__(**kwargs)
        self.cnt = int(init)
        if self.cnt < 0:
            self.cnt = 0

    def _action(self) -> int:
        try:
            return self.cnt
        finally:
            self.cnt += 1

    def action(self, *args: Any, **kwargs: Any) -> Any:
        return self._action()
