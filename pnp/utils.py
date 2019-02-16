import inspect
import logging
import os
import re
import time
from base64 import b64encode
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import partial
from functools import wraps
from threading import Timer
from typing import Union

from binaryornot.check import is_binary
from box import Box, BoxKeyError

from .validator import Validator

FILE_MODES = ['binary', 'text', 'auto']

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


logger = logging.getLogger(__name__)


class EvaluationError(Exception):
    pass


class StopCycleError(Exception):
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


def camel_to_snake(name):
    """
    Converts camelCase to snake_case.
    https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case

    >>> camel_to_snake('CamelCase')
    'camel_case'
    >>> camel_to_snake('CamelCamelCase')
    'camel_camel_case'
    >>> camel_to_snake('Camel2Camel2Case')
    'camel2_camel2_case'
    >>> camel_to_snake('getHTTPResponseCode')
    'get_http_response_code'
    >>> camel_to_snake('get2HTTPResponseCode')
    'get2_http_response_code'
    >>> camel_to_snake('HTTPResponseCode')
    'http_response_code'
    >>> camel_to_snake('HTTPResponseCodeXYZ')
    'http_response_code_xyz'

    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def wildcards_to_regex(wildcard_patterns):
    """
    Examples:

        >>> import fnmatch, re
        >>> (wildcards_to_regex(['sensor.*', 'sensor.lamp'])
        ...     == [re.compile(fnmatch.translate('sensor.*')), re.compile(fnmatch.translate('sensor.lamp'))])
        True
        >>> wildcards_to_regex('sensor.lamp') == re.compile(fnmatch.translate('sensor.lamp'))
        True
        >>> print(wildcards_to_regex(None))
        None
        >>> wildcards_to_regex([])
        []
    """

    if not wildcard_patterns:
        return wildcard_patterns
    import fnmatch
    import re
    if is_iterable_but_no_str(wildcard_patterns):
        return [re.compile(fnmatch.translate(item)) for item in wildcard_patterns]
    Validator.is_instance(str, wildcard_patterns=wildcard_patterns)
    return re.compile(fnmatch.translate(wildcard_patterns))


def include_or_exclude(item, include_regex=None, exclude_regex=None):
    """

    Returns:
        True if the item should be included; False if the item should be excluded.

    Examples:
        >>> re_all = wildcards_to_regex('sensor.*')
        >>> re1 = wildcards_to_regex('sensor.light1')
        >>> re2 = wildcards_to_regex('sensor.light2')

        >>> include_or_exclude('sensor.light1', [re1, re2])
        True
        >>> include_or_exclude('sensor.light1', [re1, re2], [re_all])
        False
        >>> include_or_exclude('sensor.light1', None, [re1])
        False
        >>> include_or_exclude('sensor.light2', None, [re1])
        True
        >>> include_or_exclude('sensor.light2', [re1], None)
        False

    """
    for regex in exclude_regex or []:
        if regex.match(item):
            return False
    for regex in include_regex or []:
        if regex.match(item):
            return True

    return include_regex is None


def transform_dict_items(dct, keys_fun=None, vals_fun=None):
    """
    Transforms keys and/or values of the given dictionary by applying the given function.

    >>> dct = {"CamelCase": "gnaaa", "foo_oool": 42}
    >>> transform_dict_items(dct, keys_fun=camel_to_snake) == {"camel_case": "gnaaa", "foo_oool": 42}
    True
    >>> transform_dict_items(dct, vals_fun=str) == {"CamelCase": "gnaaa", "foo_oool": "42"}
    True
    >>> transform_dict_items(dct, keys_fun=camel_to_snake, vals_fun=str) == {"camel_case": "gnaaa", "foo_oool": "42"}
    True
    """
    if not keys_fun and not vals_fun:
        return dct

    def apply(kv, fun):
        return kv if not fun else fun(kv)

    return {apply(k, keys_fun): apply(v, vals_fun) for k, v in dct.items()}


def is_iterable_but_no_str(candidate):
    """
    Checks if the given candidate is an iterable but not a str instance

    Example:
        >>> is_iterable_but_no_str(['a'])
        True
        >>> is_iterable_but_no_str('a')
        False
        >>> is_iterable_but_no_str(None)
        False
    """
    return hasattr(candidate, '__iter__') and not isinstance(candidate, (str, bytes))


def interruptible_sleep(wait, callback, interval=0.5):
    """

    Waits the specified amount of time. The waiting can be interrupted when the callback raises a `StopCycleError`.
    The argument `interval` defines after how much wait time the callback should be called.

    Examples:

        >>> interruptible_sleep(0.5, lambda: print("Cycle"), 0.2)  # Does perform two cycles of 0.2 secs and one 0.1
        Cycle
        Cycle
        >>> i = 0
        >>> def callback():
        ...     global i
        ...     if i == 2:
        ...         raise StopCycleError()
        ...     print("Cycle")
        ...     i = i + 1
        >>> interruptible_sleep(0.5, callback, 0.1)  # Aborts the wait after 2 cycles
        Cycle
        Cycle

    Args:
        wait (float): Wait for this amount of time, if not interrupted (some semantias as in `time.sleep(wait)`.
        interval (float): How often the callback should be called.

    Returns:
        None
    """
    wait = float(wait)
    interval = float(interval)

    complete_cycles = int(wait // interval)
    try:
        for i in range(0, complete_cycles):
            callback()  # Should raise a StopCycleError error when waiting should be aborted
            time.sleep(interval)

        time.sleep(wait % interval)
    except StopCycleError:
        pass


def make_public_protected_private_attr_lookup(attr_name, as_dict=False):
    """
    Given an attribute name this function will generate names of public, private and protected attribute names.
    The order is of lookups is always the given attr_name first and then descending by visibility (public -> proctected
    -> private)

    Examples:
        >>> make_public_protected_private_attr_lookup('my_lookup')  # Public attribute name
        ['my_lookup', '_my_lookup', '__my_lookup']
        >>> make_public_protected_private_attr_lookup('_my_lookup')  # Protected attribute name
        ['_my_lookup', 'my_lookup', '__my_lookup']
        >>> make_public_protected_private_attr_lookup('__my_lookup')  # Private attribute name
        ['__my_lookup', 'my_lookup', '_my_lookup']
        >>> l = make_public_protected_private_attr_lookup('_my_lookup', as_dict=True)
        >>> list(l.keys()), list(l.values())
        (['protected', 'public', 'private'], ['_my_lookup', 'my_lookup', '__my_lookup'])

    """
    Validator.is_instance(str, lookup_name=attr_name)
    as_dict = try_parse_bool(as_dict, default=False)
    if attr_name.startswith('__'):
        # __lookup, lookup, _lookup
        res = OrderedDict([('private', attr_name), ('public', attr_name[2:]), ('protected', attr_name[1:])])
    elif attr_name.startswith('_'):
        # _lookup, lookup, __lookup
        res = OrderedDict([('protected', attr_name), ('public', attr_name[1:]), ('private', '_' + attr_name)])
    else:
        # lookup, _lookup, __lookup
        res = OrderedDict([('public', attr_name), ('protected', '_' + attr_name), ('private', '__' + attr_name)])
    return res if as_dict else list(res.values())


def instance_lookup(instance, lookups):
    """
    Will lookup the instance for the given attribute names in `lookups`.
    Returns the first occurrence found.

    Examples:

        >>> class Foo:
        ...     def __init__(self):
        ...         self.a = 1
        ...         self.b = 2
        ...         self.c = 3
        ...         self.__a = 99
        >>> instance = Foo()
        >>> instance_lookup(instance, 'a')
        1
        >>> instance_lookup(instance, '__a')
        99
        >>> instance_lookup(instance, ['c', 'b'])
        3
        >>> instance_lookup(instance, ['d', 'b'])
        2
        >>> print(instance_lookup(instance, ['x', 'y', 'z']))
        None

    Args:
        instance: The class to lookup for the given attribute names.
        lookups: Attribute names to lookup.

    Returns:
        Returns the value of the first found attribute name in lookups. If none is found, simply None is returned.s
    """
    lookups = make_list(lookups)
    # There might be some name mangling for private attributes - add them as lookups
    privates = ['_{classname}{attrname}'.format(classname=type(instance).__name__, attrname=x)
                for x in lookups if x.startswith('__') and not x.endswith('__')]
    lookups = lookups + privates
    _Nothing = object()
    for lookup in lookups:
        val = getattr(instance, lookup, _Nothing)
        if val is not _Nothing:
            return val
    return None


def safe_eval(source, **context):
    """
    Calls the `eval` function with modified globals() and locals(). By default of `eval` the current globals() and
    locals() are passed. We do not want that behaviour because the user can make a lot of nasty things with it
    (think of a already imported `os` module...).

    Instead we pass some functions (not all) from `__builtins__` (aka the whitelist) and remove all other modules.
    The caller can pass some additional context (like variables) to the eval.

    Examples:

        >>> payload = {'foo': {'bar': 1, 'baz': 2}}
        >>> safe_eval("str(payload['foo']['bar'])", payload=payload, str=str)  # We pass some ctx the eval has access to
        '1'
        >>> import os
        >>> safe_eval("os.system('echo 0')")  # Try to access os
        Traceback (most recent call last):
        ...
        pnp.utils.EvaluationError: Failed to evaluate 'os.system('echo 0')'
        >>> safe_eval("os.system('echo 0')", os=os)  # The caller can pass the os module... if he really wants to...
        0

    Args:
        source: The source to execute.
        **context: Additional context (e.g. variables) to pass to eval.

    Returns:
        Return the result of the eval. If something went wrong it raises an error.
    """
    try:
        return eval(str(source), {'__builtins__': {}}, context)
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


def try_parse_int_float_str(candidate):
    """
    Tries to parse the given value as an int or float. If this does not work simply the string-representation of the
    candidate will be returned.

    Examples:
        >>> res = try_parse_int_float_str(5)
        >>> res, type(res)
        (5, <class 'int'>)
        >>> res = try_parse_int_float_str(5.5)
        >>> res, type(res)
        (5.5, <class 'float'>)
        >>> res = try_parse_int_float_str(5.0)
        >>> res, type(res)
        (5, <class 'int'>)
        >>> res = try_parse_int_float_str('simple_string')
        >>> res, type(res)
        ('simple_string', <class 'str'>)

    Args:
        candidate: Candidate to convert.

    """
    try:
        ffloat = float(candidate)
        return int(ffloat) if ffloat.is_integer() else ffloat
    except:
        return str(candidate)


def try_parse_bool(value, default=None):
    """
    Tries to parse the given value as a boolean. If the parsing is unsuccessful the default will be returned.

    Args:
        value: Value to parse.
        default (optional): The value to return in case the conversion is not successful.

    Returns:
        If successful the converted representation of value; otherwise the default.

    Examples:
        >>> print(try_parse_bool(1))
        True
        >>> print(try_parse_bool('true'))
        True
        >>> print(try_parse_bool('T'))
        True
        >>> print(try_parse_bool('unknown', default='Unknown'))
        Unknown
        >>> print(try_parse_bool(None, default=True))
        True
        >>> print(try_parse_bool(1.0))
        True
        >>> print(try_parse_bool(0.99))
        True
        >>> print(try_parse_bool(0.0))
        False
        >>> print(try_parse_bool(lambda x: True, default="default"))
        True
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ['t', 'true', '1', 'wahr', 'ja', 'yes', 'on']:
            return True
        elif value.lower() in ['f', 'false', '0', 'falsch', 'nein', 'no', 'off']:
            return False
        else:
            return default

    try:
        return bool(value)
    except (ValueError, TypeError):
        return default


def on_off(value):
    """
    Tries to convert the given value to a on / off literal. If conversion is not possible (unsupported datatype) it will
    silently fail and return 'off'.

    Examples:

        >>> on_off(True), on_off(False)
        ('on', 'off')
        >>> on_off('True'), on_off('False')
        ('on', 'off')
        >>> on_off(None)
        'off'
        >>> on_off(99), on_off(0)
        ('on', 'off')

    Args:
        value: The value to convert to on / off.

    Returns:
        Return 'on' if the the `value` is True or equivalent (see try_parse_bool); otherwise 'off'.
    """
    return 'on' if try_parse_bool(value, default=False) else 'off'


def get_file_mode(file_path, mode):
    """
    Returns 'rb' if mode = 'binary'.
    Returns 'r' if mode = 'text'
    Returns 'rb' or 'r' if mode = 'auto' -> Will be automatically detected.

    Example:

        >>> get_file_mode("doesn't matter", 'binary')
        'rb'
        >>> get_file_mode("doesn't matter", 'text')
        'r'
        >>> get_file_mode(__file__, 'auto')
        'r'

    Args:
        file_path: File to load.
        mode: One of ['binary', 'text', 'auto'].

    Returns:
        One of ['rb', 'r']

    """
    if mode == 'binary':
        return 'rb'
    if mode == 'text':
        return 'r'
    if mode == 'auto':
        return 'rb' if is_binary(file_path) else 'r'

    raise ValueError("Argument 'mode' is expected to be one of: auto, binary, text")


def load_file(fp, mode='auto', base64=False):
    if not isinstance(base64, bool):
        raise TypeError("Argument 'base64' is expected to be a bool, but is {}".format(type(base64)))
    mode = 'binary' if base64 else mode
    if mode not in FILE_MODES:
        raise ValueError("Argument 'mode' is expected to be one of: {}".format(FILE_MODES))

    read_mode = get_file_mode(fp, mode=mode)
    with open(fp, read_mode) as fs:
        contents = b64encode(fs.read()) if base64 else fs.read()

    return dict(file_name=os.path.basename(fp), content=contents, mode=read_mode, base64=base64)


def get_first_existing_file(*file_list):
    """
    Given is a list of possible files. The function returns the first item that exists. If none of the candidates
    exists `None` is returned.

    Examples:
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile() as ntf:
        ...     res = get_first_existing_file('idonotexists.exists', ntf.name, '/asd/dasd/ad.ad')
        >>> res == ntf.name
        True
    """
    for fp in file_list:
        if isinstance(fp, str) and os.path.isfile(fp):
            return fp
    return None


def get_bytes(stream_or_file):
    """
    Returns the bytes of the given stream or file argument. If it is a file, it will be opened in binary mode.
    Examples:
        >>> import tempfile
        >>> tmp = tempfile.NamedTemporaryFile()
        >>> print(get_bytes(tmp.name))
        b''
        >>> with open(tmp.name, 'rb') as stream:
        ...     get_bytes(stream)
        b''
        >>> get_bytes('thatonedoesnotexist')
        Traceback (most recent call last):
            ...
        ValueError: Argument 'stream_or_file' is neither a stream nor a file

    Args:
        stream_or_file: Stream or file to read the bytes from.

    Returns:
        Bytes of ``stream_or_file``
    """
    if getattr(stream_or_file, 'read', None):
        return stream_or_file.read()
    from pathlib import Path
    if Path(stream_or_file).is_file():
        with open(stream_or_file, 'rb') as file:
            return file.read()

    raise ValueError("Argument 'stream_or_file' is neither a stream nor a file")


DurationLiteral = Union[str, int]


def parse_duration_literal(literal: DurationLiteral):
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
        s = re.sub('[^0-9a-zA-Z]+', '', str(literal))
        value_str, unit = s[:-1], s[-1].lower()
        value = try_parse_int(value_str)
        if value is None or unit not in seconds_per_unit:
            raise TypeError("Interval '{}' is not a valid literal".format(literal))
        return value * seconds_per_unit[unit]


def safe_get(dct, *keys, default=None):
    """
    Get the value inside the dictionary that is accessible by the given keys or - if a key doesn't exists - the default.

    Examples:

        >>> dct = dict(nested=dict(nested1="a", nested2="b"), val="z")
        >>> safe_get(dct, "nested", "nested1")
        'a'
        >>> safe_get(dct, "nested", "unknown") is None
        True
        >>> safe_get(dct, "nested", "unknown", default="default")
        'default'
        >>> safe_get(dct) == dict(nested=dict(nested1="a", nested2="b"), val="z")
        True

    Args:
        dct: Dictionary to get the value from.
        *keys (list of hashable type): Keys to lookup.
        default (object, optional):

    Returns:
        Returns the requested value inside the probably nested dictionary. If a key does not exists, the function will
        return the default.
    """
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return default
    return dct


def get_field_mro(cls, field_name):
    """
    Goes up the mro (method resolution order) of the given class and returns the union of a given field.

    Example:

        >>> class Root:
        ...     __myfield__ = 'root'

        >>> class A(Root):
        ...     __myfield__ = ['a', 'common']

        >>> class B(Root):
        ...     __myfield__ = ['b', 'common']

        >>> class Final(A, B):
        ...     __myfield__ = 'final'

        >>> get_field_mro(Final, '__myfield__') == {'root', 'a', 'b', 'common', 'final'}
        True
        >>> get_field_mro(A, '__myfield__') == {'root', 'a', 'common'}
        True
        >>> f = Final()
        >>> get_field_mro(f, '__myfield__') == {'root', 'a', 'b', 'common', 'final'}
        True

    Args:
        cls:
        field_name:

    Returns:

    """
    res = set()
    if not hasattr(cls, '__mro__'):
        # cls might be an instance. mro is only available on classes
        if not hasattr(type(cls), '__mro__'):
            # No class, no instance ... Return empty set
            return res
        cls = type(cls)

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
        ...    def __init__(self, i=0, s="a", l=None, t=None):
        ...        self.i = i
        ...        self.s = s
        ...        self.l = l
        ...        self.t = t
        >>> dut = Demo(10, 'abc', [1, 2, 3], (1,2,3))
        >>> print(dut.__str__())
        Demo(i=10, l=[1, 2, 3], s='abc', t=(1, 2, 3))
        >>> print(eval(dut.__repr__()).__str__())
        Demo(i=10, l=[1, 2, 3], s='abc', t=(1, 2, 3))
        >>> print(dut.__repr__())
        Demo(i=10, l=[1, 2, 3], s='abc', t=(1, 2, 3))
    """
    def decorator(cls):
        def __str__(self):
            items = ["{name}={value}".format(
                name=name,
                value=vars(self)[name].__repr__()
            ) for name in [key for key in sorted(vars(self))]
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


class classproperty(property):
    """
    Decorator classproperty:
    Make class methods look like read-only class properties.
    Writing to that classproperty will not do what you expect ;-)
    Examples:
        >>> class Foo(object):
        ...     _instance = 5
        ...     @classproperty
        ...     def my_prop(cls):
        ...         return cls._instance
        >>> Foo.my_prop
        5
        >>> Foo._instance
        5
        >>> Foo._instance = 15
        >>> Foo.my_prop
        15
        >>> Foo.my_prop = 10
        >>> Foo._instance
        15
    """
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class Loggable(object):
    """
    Adds a logger property to the class to provide easy access to a configured logging instance to use.
    Example:
        >>> class NeedsLogger(Loggable):
        ...     def do(self, message):
        ...         self.logger.info(message)
        >>> dut = NeedsLogger()
        >>> dut.do('mymessage')
    """
    @classproperty
    def logger(cls):
        """
        Configures and returns a logger instance for further use.
        Returns:
            (logging.Logger)
        """
        component = "{}.{}".format(cls.__module__, cls.__name__)
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


class Debounce:
    """
    Defers a function execution until `wait` seconds have elapsed since the last time it was invoked.
    It is a way to collect multiple invokes and only really execute the last invocation.

    Examples:

        >>> results = []
        >>> def foo(counter):
        ...     results.append(counter)

        >>> dut = Debounce(foo, 0.2)  # Defers the execution for 200 milliseconds
        >>> for cnt in range(3): dut(cnt)
        >>> time.sleep(0.3)
        >>> results
        [2]

        >>> for cnt in range(4): dut(cnt)
        >>> time.sleep(0.3)
        >>> results
        [2, 3]

        >>> results.clear()
        >>> for cnt in range(3): dut(cnt)
        >>> dut.execute_now()
        >>> for cnt in range(4): dut(cnt)
        >>> time.sleep(0.3)
        >>> results
        [2, 3]



    """
    def __init__(self, fun, wait=0.5):
        Validator.is_function(fun=fun)
        self.fun = fun
        self.wait = float(wait)
        self.timer = None

    def _safe_stop_timer(self):
        if self.timer is not None:
            self.timer.cancel()

    def execute_now(self):
        # Without checking self.timer.finished.is_set(), in rare situations the actual function would get executed
        # twice
        if self.timer is not None and not self.timer.finished.is_set():
            self._safe_stop_timer()
            self.timer.function(*self.timer.args, **self.timer.kwargs)

    def __call__(self, *args, **kwargs):
        self._safe_stop_timer()
        self.timer = Timer(self.wait, self.fun, args, kwargs)
        self.timer.start()


class Singleton(object):
    """
    Derive from this class to create a singleton.
    Examples:
        >>> class Foo(Singleton):
        ...     def __init__(self, state):
        ...         self.state = state
        >>> # Instance will be created on first call ...
        >>> f = Foo('statef')
        >>> # ... and passing different arguments will not change the already created instance.
        >>> g = Foo('stateg')
        >>> f is g
        True
        >>> print(f.state)
        statef
        >>> print(g.state)
        statef
        >>> # Two ways to retrieve the singleton instance
        >>> # 1. Pretend to "create" a new instance. This will return the already created instance.
        >>> Foo() is f
        True
        >>> # Arguments work as well (but will be ignored)
        >>> Foo("i", "get", "ignored") is f
        True
        >>> # 2. The more explicit variant: Call ``instance`` on the Singleton (Explicit is good).
        >>> Foo.instance is f
        True
        >>> # You can re-initialize the instance
        >>> f.init('new_state')
        >>> print(f.state)
        new_state
        >>> print(g.state)
        new_state
    """
    def __new__(cls, *args, **kwargs):
        instance = cls.__dict__.get("__singleton__")
        if instance is None:
            # Create the singleton
            cls.__singleton__ = instance = object.__new__(cls)
            # Initialize it once.
            instance.__init__(*args, **kwargs)

            # Backup initializer ...
            cls.init = cls.__init__
            # .. and then forget about it...

            def empty_init(self, *args, **kwargs):
                pass
            cls.__init__ = empty_init
        return instance

    @classproperty
    def instance(cls):
        """
        Returns the singleton instance. If there is none yet, it will be created by calling the ``init`` method
        without any arguments.
        """
        return cls.__new__(cls)


class FileLock(object):
    """
    A file locking mechanism that has context-manager support so you can use it within a with statement.
    This implementation should be relatively cross-platform compatible cause it doesn't rely on msvcrt or fcntl
    for the locking.
    You can nest calls to ``acquire`` it will only lock the file once and release it with the last call to ``release``.
    Examples:
        >>> import tempfile
        >>> tmp = tempfile.NamedTemporaryFile()
        >>> # Basic usage with context manager
        >>> with FileLock(tmp.name) as l:
        ...     # Do something nice with the file
        ...     print(l.locked)
        True
        >>> # Basic usage w/o context manager
        >>> l = FileLock(tmp.name)
        >>> l.locked
        False
        >>> l.acquire()
        >>> try:
        ...     # Do something nice with the file
        ...     print(l.locked)
        ... finally:
        ...     l.release()
        True
        >>> print(l.locked)
        False
        >>> # Lock counter
        >>> l = FileLock(tmp.name)
        >>> with l:
        ...     print(l.lock_counter)
        ...     with l:
        ...         print(l.lock_counter)
        ...     print((l.lock_counter, l.locked))
        1
        2
        (1, True)
        >>> print((l.lock_counter, l.locked))
        (0, False)
        >>> # Blocking
        >>> with FileLock(tmp.name) as l1:
        ...     with FileLock(tmp.name, timeout=1) as l2:
        ...         pass
        Traceback (most recent call last):
        ...
        pnp.utils.FileLock.TimeoutError: Timeout occurred
    """

    class TimeoutError(Exception):
        pass

    def __init__(self, file_name, timeout=10, delay=.05):
        """
        Prepare the file locker. Specify the file to lock and optionally the maximum timeout (seconds) and the delay
        between each attempt to lock.
        Args:
            file_name: The file to lock exclusively.
            timeout: If the file is already locked by another process, this instance tries to acquire the lock
                for a maximum of `timeout` seconds.
            delay:
        """
        self.lock_counter = 0
        self.lockfile = os.path.join(os.getcwd(), "%s.lock" % file_name)
        self.file_name = file_name
        self.timeout = timeout
        self.delay = delay
        self.fd = None

    def acquire(self):
        """
        Acquires the lock, if possible. If the file is already locked, the algorithm tries to acquire the lock until
        it either gets the lock or the timeout threshold is exceeded. In case of a timeout an error is raised.
        Returns:
            None
        """
        if self.lock_counter > 0:
            # Dude, you already locked the file...
            self.lock_counter += 1
            return

        start_time = time.time()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self.lock_counter += 1
                break
            except OSError as e:
                import errno
                if e.errno != errno.EEXIST:
                    raise
                if (time.time() - start_time) >= self.timeout:
                    raise FileLock.TimeoutError("Timeout occurred")
                time.sleep(self.delay)

    def release(self):
        """
        Unlocks the file when the exclusive lock is no longer needed.
        Returns:
            None
        """
        if self.lock_counter <= 0:
            # Dude, there is no lock...
            return

        self.lock_counter -= 1
        if self.lock_counter == 0:
            os.close(self.fd)
            os.unlink(self.lockfile)

    @property
    def locked(self):
        """
        Checks whether the file is currently locked by any process.
        Returns: True if the file is currently locked (by any process, not just this one); otherwise False.
        """
        return os.path.isfile(self.lockfile)

    def __enter__(self):
        """
        Context manager acquire lock.
        Returns:
            Self
        """
        self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        """
        Context manager release.
        Args:
            type: unused
            value: unused
            traceback: unused
        Returns:
            None
        """
        self.release()

    def __del__(self):
        """
        Make sure that this instance doesn't leave a lockfile lying around when garbage collected.
        Returns:
            None
        """
        self.release()


class Parallel:
    """
    Provides an interface to easily execute functions in parallel.

    Examples:

        >>> def long_fun(r):
        ...     return r
        >>> p = Parallel(workers=2)
        >>> p(long_fun, 1, fun_key=1)
        >>> p(long_fun, 2, fun_key=2)
        >>> p(long_fun, 3, fun_key=3)
        >>> p.run_until_complete()
        ['finished', 'finished', 'finished']
        >>> p.results == {1: 1, 2: 2, 3: 3}
        True
        >>> p(long_fun, 4, fun_key=4)
        >>> p.run_until_complete()
        ['finished', 'finished', 'finished', 'finished']
        >>> p.results == {1: 1, 2: 2, 3: 3, 4: 4}
        True

        >>> memory = set()
        >>> p = Parallel(workers=2)
        >>> p(long_fun, 1, callback=lambda res: memory.add(res()))
        >>> p(long_fun, 2, callback=lambda res: memory.add(res()))
        >>> p(long_fun, 3, callback=lambda res: memory.add(res()))
        >>> p.run_until_complete()
        ['finished', 'finished', 'finished']
        >>> memory == {1, 2, 3}
        True
    """
    def __init__(self, workers=2):
        self.funcs = []
        self.workers = int(workers)
        if self.workers <= 0:
            self.workers = 1
        self._results = {}

    @property
    def results(self):
        import copy
        return copy.copy(self._results)

    def __call__(self, fun, *args, callback=None, fun_key=None, **kwargs):
        Validator.is_function(fun=fun)
        Validator.is_function(allow_none=True, callback=callback)
        self.funcs.append((fun, callback, fun_key, args, kwargs))

    def _intercept(self, future, callback, fun_key):
        if fun_key:
            try:
                self._results[fun_key] = future.result()
            except:
                import traceback
                logger.warning("Parallel result raised an error\n{}".format(traceback.format_exc()))
        if callback:
            try:
                callback(future.result)
            except:
                import traceback
                logger.warning("Parallel callback raised an error\n{}".format(traceback.format_exc()))

    def run_until_complete(self):
        self._results.clear()
        futures = []
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            for fun, cb, fun_key, args, kwargs in self.funcs:
                future = executor.submit(fun, *args, **kwargs)
                future.add_done_callback(partial(self._intercept, callback=cb, fun_key=fun_key))
                futures.append(future)

        return ['finished' if f.exception() is None else 'error' for f in futures]


class Throttle:
    """
    Decorator that prevents a function from being called more than once every
    time period.

    Example:
        >>> @Throttle(timedelta(seconds=1))
        ... def my_fun():
        ...     return "Called"
        >>> my_fun()
        'Called'
        >>> my_fun(), my_fun()
        (None, None)
        >>> time.sleep(1)
        >>> my_fun()
        'Called'

    """
    def __init__(self, delta):
        self.throttle_period = delta
        Validator.is_instance(timedelta, delta=delta)
        self.time_of_last_call = datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call

            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return fn(*args, **kwargs)

        return wrapper
