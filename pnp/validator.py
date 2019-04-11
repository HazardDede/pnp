"""Contains utility methods for validating."""
import os
from typing import Any, Callable, Iterable, List, Optional


class Validator:
    """Collection of utility methods for validating arguments / vars."""
    @staticmethod
    def _allow_none(arg_value: Any, allow_none: bool) -> bool:
        return not (allow_none and arg_value is None)

    @staticmethod
    def cast_or_none(cast_fun: Callable[[Any], Any], arg_value: Any) -> Any:
        """
        Examples:
            >>> print(Validator.cast_or_none(str, None))
            None
            >>> Validator.cast_or_none(str, 1)
            '1'
            >>> Validator.cast_or_none(int, 'a')
            Traceback (most recent call last):
            ...
            ValueError: invalid literal for int() with base 10: 'a'
        """
        return cast_fun(arg_value) if arg_value is not None else None

    @staticmethod
    def is_not_none(**kwargs: Any) -> None:
        """
        Examples:

            >>> Validator.is_not_none(arg1="foo")  # Ok
            >>> Validator.is_not_none(arg1=None)  # None
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg1' is expected to be not none
        """
        for arg_name, arg_value in kwargs.items():
            if arg_value is None:
                raise ValueError("Argument '{arg_name}' is expected to be not none".format(
                    arg_name=arg_name
                ))

    @staticmethod
    def one_not_none(**kwargs: Any) -> None:
        """
        Examples:
            >>> Validator.one_not_none(arg1=None, arg2=None, arg3='passed')
            >>> Validator.one_not_none(arg1=None, arg2=None)
            Traceback (most recent call last):
            ...
            ValueError: Arguments ['arg1', 'arg2'] expects at least one passed, but all are none
        """
        if all([x is None for x in kwargs.values()]):
            raise ValueError("Arguments {args} expects at least one passed, but all are none"
                             .format(args=sorted(list(kwargs.keys()))))

    @staticmethod
    def is_instance(*required_type: type, allow_none: bool = False, **kwargs: Any) -> None:
        """
        Examples:

            >>> Validator.is_instance(str, arg="i am a string") #  Should be ok
            >>> Validator.is_instance(str, allow_none=True, arg=None)  # Should be ok as well
            >>> Validator.is_instance(bool, arg="i am a string")  # Not ok
            Traceback (most recent call last):
            ...
            TypeError: Argument 'arg' is expected to be a (<class 'bool'>,), but is <class 'str'>
            >>> Validator.is_instance(bool, str, arg="i am a string")  # Should be ok, too
            >>> Validator.is_instance(str, bool, arg1="i am a string", arg2=True)  # Ok ...
            >>> Validator.is_instance(str, arg1="i am a string", arg2=True)  # Not ok
            Traceback (most recent call last):
            ...
            TypeError: Argument 'arg2' is expected to be a (<class 'str'>,), but is <class 'bool'>
        """
        for arg_name, arg_value in kwargs.items():
            if (Validator._allow_none(arg_value, allow_none)
                    and not isinstance(arg_value, required_type)):
                raise TypeError(
                    "Argument '{arg_name}' is expected to be a {required_type}"
                    ", but is {actual_type}".format(
                        arg_name=arg_name,
                        required_type=required_type,
                        actual_type=type(arg_value)
                    ))

    @staticmethod
    def is_non_negative(allow_none: bool = False, **kwargs: Any) -> None:
        """
        Examples:
            >>> Validator.is_non_negative(arg=0)
            >>> Validator.is_non_negative(arg=1)
            >>> Validator.is_non_negative(arg=-0.01)
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg' is expected to be greater or equal to zero, but it is not
            >>> Validator.is_non_negative(arg="a")
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg' is not numeric (float, int, ...)
        """
        for arg_name, arg_value in kwargs.items():
            try:
                arg_value = float(arg_value)
            except (TypeError, ValueError):
                raise ValueError("Argument '{arg_name}' is not numeric (float, int, ...)".format(
                    arg_name=arg_name
                ))

            if Validator._allow_none(arg_value, allow_none) and arg_value < 0.0:
                raise ValueError(
                    "Argument '{arg_name}' is expected to be greater or equal to zero"
                    ", but it is not".format(arg_name=arg_name))

    @staticmethod
    def one_of(possible: Iterable[Any], allow_none: bool = False, **kwargs: Any) -> None:
        """
        Examples:
            >>> Validator.one_of(['a', 'b', 'c'], arg='a')
            >>> Validator.one_of(['a', 'b', 'c'], allow_none=True, arg='a', arg2=None)
            >>> Validator.one_of(['a', 'b', 'c'], arg='z')
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg' is expected to be one of ['a', 'b', 'c'], but is 'z'
            >>> Validator.one_of(['a', 'b', 'c'], arg1='a', arg2='z')
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg2' is expected to be one of ['a', 'b', 'c'], but is 'z'
        """
        Validator.is_instance(list, tuple, possible=possible)
        for arg_name, arg_value in kwargs.items():
            if Validator._allow_none(arg_value, allow_none) and arg_value not in possible:
                raise ValueError(
                    "Argument '{arg_name}' is expected to be one of {possible}, "
                    "but is '{arg_value}'".format(
                        arg_name=arg_name, possible=possible, arg_value=arg_value
                    )
                )

    @staticmethod
    def subset_of(possible: Iterable[Any], allow_none: bool = False, **kwargs: Any) -> None:
        """
        Examples:

            >>> Validator.subset_of(['a', 'b', 'c'], arg='a')
            >>> Validator.subset_of(['a', 'b', 'c'], arg=('a', 'b'))
            >>> Validator.subset_of(['a', 'b', 'c'], arg=('a', 'b'), arg2='c')
            >>> Validator.subset_of(['a', 'b', 'c'], arg='d')
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg' is expected to be a subset of ['a', 'b', 'c'], but is 'd'
            >>> Validator.subset_of(['a', 'b', 'c'], allow_none=True, arg1=None, arg2=None)
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

        Validator.is_instance(list, tuple, possible=possible)
        for arg_name, arg_value in kwargs.items():
            if (Validator._allow_none(arg_value, allow_none)
                    and not set(make_list(arg_value) or set()) <= set(possible)):
                raise ValueError(
                    "Argument '{arg_name}' is expected to be a subset of {possible}, "
                    "but is '{arg_value}'".format(
                        arg_name=arg_name, possible=possible, arg_value=arg_value
                    )
                )

    @staticmethod
    def is_directory(allow_none: bool = False, **kwargs: Any) -> None:
        """
        Examples:
            >>> Validator.is_directory(arg='/tmp')
            >>> Validator.is_directory(arg='/thisonedoesnotexists')
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg' is expected to be a directory, but is '/thisonedoesnotexists'
        """
        for arg_name, arg_value in kwargs.items():
            if (Validator._allow_none(arg_value, allow_none)
                    and not os.path.isdir(arg_value)):
                raise ValueError(
                    "Argument '{arg_name}' is expected to be a directory, "
                    "but is '{arg_value}'".format(arg_name=arg_name, arg_value=arg_value)
                )

    @staticmethod
    def is_file(allow_none: bool = False, **kwargs: Any) -> None:
        """
        Examples:
            >>> import tempfile
            >>> with tempfile.NamedTemporaryFile() as tmpf:
            ...     Validator.is_file(arg=tmpf.name)
            >>> Validator.is_file(arg='/doesnotexist.txt')
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg' is expected to be a file, but is '/doesnotexist.txt'
        """
        for arg_name, arg_value in kwargs.items():
            if Validator._allow_none(arg_value, allow_none) and not os.path.isfile(arg_value):
                raise ValueError(
                    "Argument '{arg_name}' is expected to be a file, "
                    "but is '{arg_value}'".format(
                        arg_name=arg_name, arg_value=arg_value
                    )
                )

    @staticmethod
    def is_function(allow_none: bool = False, **kwargs: Any) -> None:
        """
        Examples:
            >>> def foo():
            ...     pass
            >>> Validator.is_function(foo=foo)
            >>> Validator.is_function(bar='bar')
            Traceback (most recent call last):
            ...
            TypeError: Argument 'bar' is expected to be a function/callable, but is '<class 'str'>'
            >>> Validator.is_function(baz=lambda: True)
        """
        for arg_name, arg_value in kwargs.items():
            if Validator._allow_none(arg_value, allow_none) and not callable(arg_value):
                arg_type = type(arg_value)
                raise TypeError(
                    "Argument '{arg_name}' is expected to be a function/callable, "
                    "but is '{arg_type}'".format(
                        arg_name=arg_name, arg_type=arg_type
                    )
                )

    @staticmethod
    def is_iterable_but_no_str(allow_none: bool = False, **kwargs: Any) -> None:
        """
        Examples:
            >>> Validator.is_iterable_but_no_str(l=[])
            >>> Validator.is_iterable_but_no_str(t=("a", "b"))
            >>> Validator.is_iterable_but_no_str(s="abc")
            Traceback (most recent call last):
            ...
            TypeError: Argument 's' is expected to be a non-str iterable, but is '<class 'str'>'

        """
        def is_iterable_but_no_str(candidate: Any) -> bool:
            return hasattr(candidate, '__iter__') and not isinstance(candidate, (str, bytes))

        for arg_name, arg_value in kwargs.items():
            if (Validator._allow_none(arg_value, allow_none)
                    and not is_iterable_but_no_str(arg_value)):
                arg_type = type(arg_value)
                raise TypeError(
                    "Argument '{arg_name}' is expected to be a non-str iterable, "
                    "but is '{arg_type}'".format(
                        arg_name=arg_name, arg_type=arg_type
                    )
                )
