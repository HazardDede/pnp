"""Contains simple user-defined functions."""

from pnp.plugins.udf import UserDefinedFunction


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


class FormatSize(UserDefinedFunction):
    """
    Returns the size of a file (or whatever) as a human readable size (e.g. bytes, KB, MB, GB, TB,
    PB). The input is expected to be at byte scale.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/udf/simple.FormatSize/index.md

    Example:
        >>> dut = FormatSize(name='doctest')
        >>> dut.action(0)
        '0 byte'
        >>> dut.action(1)
        '1 byte'
        >>> dut.action(5555.5)
        '5 KB'
        >>> dut.action(4672512)
        '4.5 MB'
        >>> dut.action(45548128174.08)
        '42.42 GB'
        >>> dut.action(-42)
        Traceback (most recent call last):
        ...
        ValueError: No negative values supported.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _human_size(size_bytes):
        """
        format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
        Note that bytes/KB will be reported in whole numbers but MB and above will have
        greater precision e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc

        Taken from:
        https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
        """
        num = float(size_bytes)
        if num < 0:
            raise ValueError("No negative values supported.")

        if num <= 1:
            # because I really hate unnecessary plurals
            return "%d byte" % num

        suffixes_table = [('bytes', 0), ('KB', 0), ('MB', 1), ('GB', 2), ('TB', 2), ('PB', 2)]

        # Will at least run once
        for suffix, precision in suffixes_table:
            if num < 1024.0:
                break
            num /= 1024.0

        if precision == 0:
            formatted_size = "%d" % num
        else:
            formatted_size = str(round(num, ndigits=precision))

        return "%s %s" % (formatted_size, suffix)

    def action(self, size_in_bytes):  # pylint: disable=arguments-differ
        return self._human_size(size_in_bytes)


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

    def __init__(self, init=_MISSING, **kwargs):
        super().__init__(**kwargs)
        self.current = init

    def action(self, new_memory=_MISSING):  # pylint: disable=arguments-differ
        try:
            if self.current is self._MISSING:
                return None if new_memory is self._MISSING else new_memory

            return self.current
        finally:
            if new_memory is not self._MISSING:
                self.current = new_memory
