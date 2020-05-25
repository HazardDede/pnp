"""Contains utility methods for validating."""
import os
from typing import Any, Iterable, List, Optional

from typeguard import typechecked


@typechecked
def all_items(item_type: type, **kwargs: Iterable[Any]) -> None:
    """
    Examples:
        >>> all_items(str, a=['a', 'b', 'c'])
        >>> all_items(int, a=[1, 2, 3])
        >>> all_items(int, b=[1, 's', 3])
        Traceback (most recent call last):
        ...
        TypeError: Item value at pos 1 of argument 'b' is expected to be a <class 'int'>,\
 but is <class 'str'>
    """
    is_iterable_but_no_str(**kwargs)
    for arg_name, arg_val in kwargs.items():
        for i, item in enumerate(arg_val):
            if not isinstance(item, item_type):
                raise TypeError(
                    "Item value at pos {} of argument '{}' is expected to be a {}, "
                    "but is {}".format(
                        i, arg_name, item_type, type(item)
                    )
                )


@typechecked
def attrs_validator_dict_items(
    instance: Any, attrib: Any, val: Any, key_type: type, val_type: type
) -> Any:
    """Attrs helper function to validate a dictionary and it's items."""
    _ = instance  # Fake usage

    if not isinstance(val, dict):
        raise TypeError(
            "Argument {} is expected to be a dictionary, but is {}".format(attrib.name, type(val))
        )
    for i, (key, value) in enumerate(val.items()):
        if not isinstance(key, key_type):
            raise TypeError(
                "Key at {} position is expected to be a {}, but is {}".format(
                    i, key_type, type(value)
                )
            )
        if not isinstance(value, val_type):
            raise TypeError(
                "Value at {} position is expected to be a {}, but is {}".format(
                    i, val_type, type(value)
                )
            )
    return val


@typechecked
def attrs_validate_list_items(instance: Any, attrib: Any, val: Any, item_type: type) -> Any:
    """Attrs helper function to validate a list and it's items."""
    _ = instance

    is_iterable_but_no_str(**{attrib.name: val})
    for i, item in enumerate(val):
        if not isinstance(item, item_type):
            raise TypeError(
                "Item value at {} position is expected to be a {}, but is {}".format(
                    i, item_type, type(item)
                )
            )
    return val


def is_directory(**kwargs: Any) -> None:
    """
    Examples:
        >>> is_directory(arg='/tmp')
        >>> is_directory(arg='/thisonedoesnotexists')
        Traceback (most recent call last):
        ...
        ValueError: Argument 'arg' is expected to be a directory, but is '/thisonedoesnotexists'
    """
    for arg_name, arg_value in kwargs.items():
        if not os.path.isdir(arg_value):
            raise ValueError(
                "Argument '{arg_name}' is expected to be a directory, "
                "but is '{arg_value}'".format(arg_name=arg_name, arg_value=arg_value)
            )


def is_file(**kwargs: Any) -> None:
    """
    Examples:
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile() as tmpf:
        ...     is_file(arg=tmpf.name)
        >>> is_file(arg='/doesnotexist.txt')
        Traceback (most recent call last):
        ...
        ValueError: Argument 'arg' is expected to be a file, but is '/doesnotexist.txt'
    """
    for arg_name, arg_value in kwargs.items():
        if not os.path.isfile(str(arg_value)):
            raise ValueError(
                "Argument '{arg_name}' is expected to be a file, "
                "but is '{arg_value}'".format(
                    arg_name=arg_name, arg_value=arg_value
                )
            )


def is_function(**kwargs: Any) -> None:
    """
    Examples:
        >>> def foo():
        ...     pass
        >>> is_function(foo=foo)
        >>> is_function(bar='bar')
        Traceback (most recent call last):
        ...
        TypeError: Argument 'bar' is expected to be a function/callable, but is '<class 'str'>'
        >>> is_function(baz=lambda: True)
    """
    for arg_name, arg_value in kwargs.items():
        if not callable(arg_value):
            arg_type = type(arg_value)
            raise TypeError(
                "Argument '{arg_name}' is expected to be a function/callable, "
                "but is '{arg_type}'".format(
                    arg_name=arg_name, arg_type=arg_type
                )
            )


@typechecked
def is_instance(*required_types: type, allow_none: bool = False, **kwargs: Any) -> None:
    """
    Examples:

        >>> is_instance(str, arg="i am a string") #  Should be ok
        >>> is_instance(str, allow_none=True, arg=None)  # Should be ok as well
        >>> is_instance(bool, arg="i am a string")  # Not ok
        Traceback (most recent call last):
        ...
        TypeError: Argument 'arg' is expected to be a (<class 'bool'>,), but is <class 'str'>
        >>> is_instance(bool, str, arg="i am a string")  # Should be ok, too
        >>> is_instance(str, bool, arg1="i am a string", arg2=True)  # Ok ...
        >>> is_instance(str, arg1="i am a string", arg2=True)  # Not ok
        Traceback (most recent call last):
        ...
        TypeError: Argument 'arg2' is expected to be a (<class 'str'>,), but is <class 'bool'>
    """
    for arg_name, arg_value in kwargs.items():
        if not (allow_none and arg_value is None) and not isinstance(arg_value, required_types):
            raise TypeError(
                "Argument '{arg_name}' is expected to be a {required_type}"
                ", but is {actual_type}".format(
                    arg_name=arg_name,
                    required_type=required_types,
                    actual_type=type(arg_value)
                ))


def is_iterable_but_no_str(**kwargs: Any) -> None:
    """
    Examples:
        >>> is_iterable_but_no_str(l=[])
        >>> is_iterable_but_no_str(t=("a", "b"))
        >>> is_iterable_but_no_str(s="abc")
        Traceback (most recent call last):
        ...
        TypeError: Argument 's' is expected to be a non-str iterable, but is '<class 'str'>'

    """
    for arg_name, arg_value in kwargs.items():
        # Cannot import from utils -> cyclic dependency
        if not hasattr(arg_value, '__iter__') or isinstance(arg_value, (str, bytes)):
            arg_type = type(arg_value)
            raise TypeError(
                "Argument '{arg_name}' is expected to be a non-str iterable, "
                "but is '{arg_type}'".format(
                    arg_name=arg_name, arg_type=arg_type
                )
            )


def one_not_none(**kwargs: Any) -> None:
    """
    Examples:
        >>> one_not_none(arg1=None, arg2=None, arg3='passed')
        >>> one_not_none(arg1=None, arg2=None)
        Traceback (most recent call last):
        ...
        ValueError: Arguments ['arg1', 'arg2'] expects at least one passed, but all are none
    """
    if all([x is None for x in kwargs.values()]):
        raise ValueError(
            "Arguments {args} expects at least one passed, but all are none".format(
                args=sorted(list(kwargs.keys()))
            )
        )


@typechecked
def one_of(possible: Iterable[Any], **kwargs: Any) -> None:
    """
    Examples:
        >>> one_of(['a', 'b', 'c'], arg='a')
        >>> one_of(['a', 'b', 'c'], arg='z')
        Traceback (most recent call last):
        ...
        ValueError: Argument 'arg' is expected to be one of ['a', 'b', 'c'], but is 'z'
        >>> one_of(['a', 'b', 'c'], arg1='a', arg2='z')
        Traceback (most recent call last):
        ...
        ValueError: Argument 'arg2' is expected to be one of ['a', 'b', 'c'], but is 'z'
    """
    for arg_name, arg_value in kwargs.items():
        if arg_value not in possible:
            raise ValueError(
                "Argument '{arg_name}' is expected to be one of {possible}, "
                "but is '{arg_value}'".format(
                    arg_name=arg_name, possible=possible, arg_value=arg_value
                )
            )


@typechecked
def subset_of(possible: Iterable[Any], **kwargs: Any) -> None:
    """
    Examples:

        >>> subset_of(['a', 'b', 'c'], arg='a')
        >>> subset_of(['a', 'b', 'c'], arg=('a', 'b'))
        >>> subset_of(['a', 'b', 'c'], arg=('a', 'b'), arg2='c')
        >>> subset_of(['a', 'b', 'c'], arg='d')
        Traceback (most recent call last):
        ...
        ValueError: Argument 'arg' is expected to be a subset of ['a', 'b', 'c'], but is 'd'
    """
    def make_list(lst: Any) -> Optional[List[Any]]:
        if lst is None:
            return None
        if isinstance(lst, list):
            return lst
        if isinstance(lst, dict):
            return [lst]
        if hasattr(lst, '__iter__') and not isinstance(lst, str):
            return list(lst)
        return [lst]

    for arg_name, arg_value in kwargs.items():
        if not set(make_list(arg_value) or set()) <= set(possible):
            raise ValueError(
                "Argument '{arg_name}' is expected to be a subset of {possible}, "
                "but is '{arg_value}'".format(
                    arg_name=arg_name, possible=possible, arg_value=arg_value
                )
            )
