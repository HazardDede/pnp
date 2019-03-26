"""Contains simple user-defined functions."""

from . import UserDefinedFunction


class Counter(UserDefinedFunction):
    """
    Memories a counter value which is increased everytime you call the udf.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/udf/simple.Counter/index.md

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
    def __init__(self, init=0, **kwargs):
        super().__init__(**kwargs)
        self.cnt = int(init)
        if self.cnt < 0:
            self.cnt = 0

    def action(self):  # pylint: disable=arguments-differ
        try:
            return self.cnt
        finally:
            self.cnt += 1


class Memory(UserDefinedFunction):
    """
    Returns a previously memorized value when called.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/udf/simple.Memory/index.md

    Example:

        >>> dut = Memory(name='doctest', init='foo')
        >>> dut(), dut(new_memory='baz'), dut()
        ('foo', 'foo', 'baz')
    """
    _MISSING = object()

    def __init__(self, init=None, **kwargs):
        super().__init__(**kwargs)
        self.init = init

    def action(self, new_memory=_MISSING):  # pylint: disable=arguments-differ
        try:
            return self.init
        finally:
            if new_memory is not self._MISSING:
                self.init = new_memory
