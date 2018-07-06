import os


class Validator:
    @staticmethod
    def _allow_none(arg_value, allow_none):
        return not (allow_none and arg_value is None)

    @staticmethod
    def cast_or_none(cast_fun, arg_value):
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
    def is_not_none(**kwargs):
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
                raise ValueError("Argument '{arg_name}' is expected to be not none".format(**locals()))

    @staticmethod
    def one_not_none(**kwargs):
        """
        Examples:
            >>> Validator.one_not_none(arg1=None, arg2=None, arg3='passed')
            >>> Validator.one_not_none(arg1=None, arg2=None, arg3=None)
            Traceback (most recent call last):
            ...
            ValueError: Arguments ['arg1', 'arg2', 'arg3'] expects at least one passed, but all are none
        """
        if all([x is None for x in kwargs.values()]):
            raise ValueError("Arguments {args} expects at least one passed, but all are none"
                             .format(args=sorted(list(kwargs.keys()))))

    @staticmethod
    def is_instance(*required_type, allow_none=False, **kwargs):
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
            if Validator._allow_none(arg_value, allow_none) and not isinstance(arg_value, required_type):
                raise TypeError("Argument '{arg_name}' is expected to be a {required_type}"
                                ", but is {actual_type}".format(**locals(), actual_type=type(arg_value)))

    @staticmethod
    def is_non_negative(allow_none=False, **kwargs):
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
                raise ValueError("Argument '{arg_name}' is not numeric (float, int, ...)".format(**locals()))

            if Validator._allow_none(arg_value, allow_none) and arg_value < 0.0:
                raise ValueError("Argument '{arg_name}' is expected to be greater or equal to zero"
                                 ", but it is not".format(**locals()))

    @staticmethod
    def one_of(possible, allow_none=False, **kwargs):
        """
        Examples:
            >>> Validator.one_of(['a', 'b', 'c'], arg='a')
            >>> Validator.one_of(['a', 'b', 'c'], allow_none=True, arg='a', arg2=None)  # Should be ok as well
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
                raise ValueError("Argument '{arg_name}' is expected to be one of {possible}, "
                                 "but is '{arg_value}'".format(**locals()))

    @staticmethod
    def subset_of(possible, allow_none=False, **kwargs):
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
        from .utils import make_list
        Validator.is_instance(list, tuple, possible=possible)
        for arg_name, arg_value in kwargs.items():
            if Validator._allow_none(arg_value, allow_none) and not (set(make_list(arg_value)) <= set(possible)):
                raise ValueError("Argument '{arg_name}' is expected to be a subset of {possible}, but is '{arg_value}'"
                                 .format(**locals()))

    @staticmethod
    def is_directory(allow_none=False, **kwargs):
        """
        Examples:
            >>> Validator.is_directory(arg='/tmp')
            >>> Validator.is_directory(arg='/thisonedoesnotexists')
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg' is expected to be a directory, but is '/thisonedoesnotexists'
        """
        for arg_name, arg_value in kwargs.items():
            if Validator._allow_none(arg_value, allow_none) and not os.path.isdir(arg_value):
                raise ValueError("Argument '{arg_name}' is expected to be a directory, "
                                 "but is '{arg_value}'".format(**locals()))

    @staticmethod
    def is_file(allow_none=False, **kwargs):
        """
        Examples:
            >>> import tempfile
            >>> with tempfile.NamedTemporaryFile() as tmpf:
            ...     Validator.is_file(arg=tmpf.name)
            >>> Validator.is_file(arg='/thisonedoesnotexists.txt')
            Traceback (most recent call last):
            ...
            ValueError: Argument 'arg' is expected to be a file, but is '/thisonedoesnotexists.txt'
        """
        for arg_name, arg_value in kwargs.items():
            if Validator._allow_none(arg_value, allow_none) and not os.path.isfile(arg_value):
                raise ValueError("Argument '{arg_name}' is expected to be a file, "
                                 "but is '{arg_value}'".format(**locals()))

    @staticmethod
    def is_function(allow_none=False, **kwargs):
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
                raise TypeError("Argument '{arg_name}' is expected to be a function/callable, "
                                "but is '{arg_type}'".format(**locals()))
