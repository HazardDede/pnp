import inspect
import logging
import re

from box import Box, BoxKeyError


class EvaluationError(Exception):
    pass


def make_list(item_or_items):
    """
    Makes a list out of the given items.
    Examples:
        >>> make_list(1)
        [1]
        >>> make_list('str')
        ['str']
        >>> make_list(('i', 'am', 'a', 'tuple'))
        ['i', 'am', 'a', 'tuple']
        >>> print(make_list(None))
        None
        >>> # An instance of lists is unchanged
        >>> l = ['i', 'am', 'a', 'list']
        >>> l_res = make_list(l)
        >>> l_res
        ['i', 'am', 'a', 'list']
        >>> l_res is l
        True

    Args:
        item_or_items: A single value or an iterable.
    Returns:
        Returns the given argument as an list.
    """
    if item_or_items is None:
        return None
    if isinstance(item_or_items, list):
        return item_or_items
    if isinstance(item_or_items, dict):
        return [item_or_items]
    if hasattr(item_or_items, '__iter__') and not isinstance(item_or_items, str):
        return list(item_or_items)
    return [item_or_items]


def safe_eval(source, **context):
    whitelist = {
        "abs": abs,
        "bool": bool,
        "dict": dict,
        "float": float,
        "getattr": getattr,
        "hasattr": hasattr,
        "hash": hash,
        "int": int,
        "isinstance": isinstance,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "ord": ord,
        "pow": pow,
        "reversed": reversed,
        "round": round,
        "sorted": sorted,
        "str": str,
        "zip": zip
    }
    whitelist.update(context)
    try:
        return eval(
            source,
            {'__builtins__': {}},
            whitelist
        )
    except Exception as exc:
        raise EvaluationError("Failed to evaluate '{source}'".format(**locals())) from exc


def try_parse_int(candidate):
    """
    Convert the given candidate to int. If it fails None is returned.

    Example:

        >>> type(try_parse_int(1))  # int will still be int
        <class 'int'>
        >>> type(try_parse_int("15"))
        <class 'int'>
        >>> print(try_parse_int("a"))
        None

    Args:
        candidate: The candidate to convert.

    Returns:
        Returns the converted candidate if convertible; otherwise None.

    """
    try:
        return int(candidate)
    except (ValueError, TypeError):
        return None


def parse_duration_literal(literal):
    """
    Converts duration literals as '1m', '1h', and so on to an actual duration in seconds.
    Supported are 's' (seconds), 'm' (minutes), 'h' (hours), 'd' (days) and 'w' (weeks).

    Examples:

        >>> parse_duration_literal(60)  # Int will be interpreted as seconds
        60
        >>> parse_duration_literal('10')  # Any int convertible will be interpreted as seconds
        10
        >>> parse_duration_literal('20s')  # Seconds literal
        20
        >>> parse_duration_literal('2m')  # Minutes literal
        120
        >>> parse_duration_literal('1h')  # Hours literal
        3600
        >>> parse_duration_literal('1d')  # Days literal
        86400
        >>> parse_duration_literal('1w')  # Weeks literal
        604800
        >>> parse_duration_literal('invalid')  # Invalid will raise an error
        Traceback (most recent call last):
        ...
        TypeError: Interval 'invalid' is not a valid literal

    Args:
        literal: Literal to parse.

    Returns:
        Returns the converted literal's duration in seconds. If conversion is not possible
        an exception is raised.
    """
    try:
        # if successful we got seconds
        return int(literal)
    except:  # pylint: disable=broad-except
        # We have to check for s, m, h, d, w suffix
        seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        # Remove all non-alphanumeric letters
        s = re.sub('[^0-9a-zA-Z]+', '', literal)
        value_str, unit = s[:-1], s[-1].lower()
        value = try_parse_int(value_str)
        if value is None or unit not in seconds_per_unit:
            raise TypeError("Interval '{}' is not a valid literal".format(literal))
        return value * seconds_per_unit[unit]


def get_field_mro(cls, field_name):
    res = set()
    for c in inspect.getmro(cls):
        values_ = getattr(c, field_name, None)
        if values_ is not None:
            res = res.union(set(make_list(values_)))
    return res


def auto_str(__repr__=False):
    """
    Use this decorator to auto implement __str__() and optionally __repr__() methods on classes.

    Args:
        __repr__ (bool): If set to true, the decorator will auto-implement the __repr__() method as well.

    Returns:
        callable: Decorating function.

    Note:
        There are known issues with self referencing (self.s = self). Recursion will be identified by the python
        interpreter and will do no harm, but it will actually not work.
        A eval(class.__repr__()) will obviously not work, when there are attributes that are not part of the
        __init__'s arguments.

    Example:
        >>> @auto_str(__repr__=True)
        ... class Demo(object):
        ...    def __init__(self, i=0, s="a", l=None, d=None):
        ...        self.i = i
        ...        self.s = s
        ...        self.l = l
        ...        self.d = d
        >>> dut = Demo(10, 'abc', [1, 2, 3], {'a': 1, 'b': 2})
        >>> print(dut.__str__())
        Demo(i=10, s='abc', l=[1, 2, 3], d={'a': 1, 'b': 2})
        >>> print(eval(dut.__repr__()).__str__())
        Demo(i=10, s='abc', l=[1, 2, 3], d={'a': 1, 'b': 2})
        >>> print(dut.__repr__())
        Demo(i=10, s='abc', l=[1, 2, 3], d={'a': 1, 'b': 2})
    """
    def decorator(cls):
        def __str__(self):
            items = ["{name}={value}".format(
                name=name,
                value=value.__repr__()
            ) for name, value in vars(self).items()
                if name not in get_field_mro(self.__class__, '__auto_str_ignore__')]
            return "{clazz}({items})".format(
                clazz=str(type(self).__name__),
                items=', '.join(items)
            )
        cls.__str__ = __str__
        if __repr__:
            cls.__repr__ = __str__

        return cls

    return decorator


def auto_str_ignore(ignore_list):
    """
    Use this decorator to suppress any fields that should not be part of the dynamically created
    `__str__` or `__repr__` function of `auto_str`.

    Example:

        >>> @auto_str()
        ... @auto_str_ignore(["l", "d"])
        ... class Demo(object):
        ...    def __init__(self, i=0, s="a", l=None, d=None):
        ...        self.i = i
        ...        self.s = s
        ...        self.l = l
        ...        self.d = d
        >>> dut = Demo(10, 'abc', [1, 2, 3], {'a': 1, 'b': 2})
        >>> print(str(dut))
        Demo(i=10, s='abc')

    Args:
        ignore_list: List or item of the fields to suppress by `auto_str`.

    Returns:
        Returns a decorator.
    """
    def decorator(cls):
        ignored = make_list(ignore_list)
        cls.__auto_str_ignore__ = ignored
        return cls
    return decorator


class Loggable(object):
    """
    Adds a logger property to the class to provide easy access to a configured logging instance to use.
    Example:
        >>> class NeedsLogger(Loggable):
        ...     def do(self, message):
        ...         self.logger.info(message)
    """
    @property
    def logger(self):
        """
        Configures and returns a logger instance for further use.
        Returns:
            (logging.Logger)
        """
        component = "{}.{}".format(type(self).__module__, type(self).__name__)
        return logging.getLogger(component)


class FallbackBox(Box):
    """
    In some cases we want to handle integers and floats as string when accessing
    a boxed dictionary. For example we would like to mimic access paths like the zway api can:
        devices[19].instances[0].commandClasses[49].data[3].val.value
    In this case all int looking ones are actual string keys. But for plugins we want it
    as easy as possible. So we first take the key as it is to access the data, but when it raises a `KeyError`
    we cast the key to str and try it again to access the key as a fallback.

    Examples:

        >>> d = {'devices': {'1': {'instances': {'0': 'instance0', 1: 'instance1'}}}}
        >>> dut = FallbackBox(d)
        >>> dut.devices[1].instances[0]  # devices.1 is a syntax error, cause 1 is not a valid identifier
        'instance0'
        >>> dut.devices[1].instances[1]
        'instance1'
    """
    def __getitem__(self, item, _ignore_default=False):
        try:
            return super().__getitem__(item, _ignore_default=_ignore_default)
        except BoxKeyError as ke:
            if isinstance(item, (int, float)):
                return super().__getitem__(str(item), _ignore_default=_ignore_default)
            raise ke
