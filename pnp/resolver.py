import inspect
import os
from functools import partial

from .utils import make_list

Missing = object()


def get_class_that_defined_method(meth):
    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                return cls
        meth = meth.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)


# Helper function to resolve argument from environment
def envargs_fun(name, value, defaults, prefix=None, cls=None):
    if value is not Missing:
        return value
    lookup = name.upper()
    if prefix is not None:
        lookup = prefix.upper() + '_' + lookup
    newval = os.environ.get(lookup, None) or defaults.get(name, Missing)
    if newval is Missing:
        raise Exception("Cannot resolve argument '{}' of {}. Try to set environment variable '{}'".format(
            name, cls, lookup))
    return newval


def static_fun(static_value, name, value, defaults, prefix=None, cls=None):
    if value is not Missing:
        return value
    if name in defaults:
        return defaults[name]
    return static_value


def resolver(resolve_fun, ignore):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            # Init - ignore will always include self and cls
            ignore_args = {'self', 'cls'}
            if ignore is not None:
                ignore_args = set(make_list(ignore))

            # Argument name-value pairs
            sig = inspect.getargspec(fun)
            defaults = {}
            if sig.defaults is not None:
                defaults = {k: v for k, v in list(zip(sig.args[-len(sig.defaults):], sig.defaults))}
            named_args = list(zip(sig.args, args))
            unset = (set(sig.args)
                     - set([name for name, _ in named_args])
                     .union(set([name for name, _ in kwargs.items()])))
            for u in unset:
                kwargs[u] = Missing

            mclazz = get_class_that_defined_method(fun)
            # prefix + argname will determine the name of the environment variable (all uppercased)
            # Example: prefix = 'zway' + argname 'host' will result into ZWAY_HOST
            prefix = getattr(mclazz, '__prefix__', None)

            # Create ignore list - go up all superclasses as well
            # Ignore means that no value resolution will take place
            for c in inspect.getmro(mclazz):
                ignore_from_clazz = getattr(c, '__ignore__', None)
                if ignore_from_clazz is not None:
                    ignore_args = ignore_args.union(set(make_list(ignore_from_clazz)))

            def call_resolve(name, value):
                if name in ignore_args:
                    return value
                return resolve_fun(name, value, defaults, prefix, mclazz)

            # new args + kwargs to inject to wrapped function
            new_kwargs = {name: call_resolve(name, value) for name, value in named_args}
            new_kwargs.update({name: call_resolve(name, value) for name, value in kwargs.items()})

            # call with new kwargs (ignore missing ones)
            return fun(**{k: v for k, v in new_kwargs.items() if v is not Missing})
        return wrapper
    return decorator


envargs = partial(resolver, envargs_fun)
static = partial(resolver, partial(static_fun, 5))