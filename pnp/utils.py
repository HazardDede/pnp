import inspect
import logging
import re


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
    if hasattr(item_or_items, '__iter__') and not isinstance(item_or_items, str):
        return list(item_or_items)
    return [item_or_items]


def try_parse_int(candidate):
    try:
        return int(candidate)
    except (ValueError, TypeError):
        return None


def parse_interval(candidate):
    try:
        # if successful we got seconds
        return int(candidate)
    except:
        # We have to check for s, m, h, d, w suffix
        seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        # Remove all non-alphanumeric letters
        s = re.sub('[^0-9a-zA-Z]+', '', candidate)
        value_str, unit = s[:-1], s[-1].lower()
        value = try_parse_int(value_str)
        if value is None or unit not in seconds_per_unit:
            raise TypeError("Interval '{}' is not a valid interval".format(candidate))
        return value * seconds_per_unit[unit]


def get_field_mro(cls, field_name):
    res = set()
    for c in inspect.getmro(cls):
        values_ = getattr(c, field_name, None)
        if values_ is not None:
            res = res.union(set(make_list(values_)))
    return res


def auto_str_ignore(ignore_list):
    def decorator(cls):
        ignored = make_list(ignore_list)
        cls.__auto_str_ignore__ = ignored
        return cls
    return decorator


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