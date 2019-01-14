from . import UserDefinedFunction


class Counter(UserDefinedFunction):
    """
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

    def action(self):
        try:
            return self.cnt
        finally:
            self.cnt += 1
