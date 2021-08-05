"""UDF: simple.FormatSize"""
from typing import Any

from pnp.plugins.udf import UserDefinedFunction


class FormatSize(UserDefinedFunction):
    """
    Returns the size of a file (or whatever) as a human readable size (e.g. bytes, KB, MB, GB, TB,
    PB). The input is expected to be at byte scale.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-formatsize

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
    @staticmethod
    def _human_size(size_bytes: float) -> str:
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

    def _action(self, size_in_bytes: float) -> str:
        return self._human_size(size_in_bytes)

    def action(self, *args: Any, **kwargs: Any) -> Any:
        return self._action(*args, **kwargs)
