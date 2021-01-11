"""Base stuff for pushes."""

import asyncio
import copy
import functools
import inspect
from abc import abstractmethod
from typing import Any, Callable, Optional, Dict, Iterable, Union, cast, List, Tuple, Awaitable

from pnp import utils
from pnp import validator
from pnp.plugins import Plugin
from pnp.shared.async_ import run_sync
from pnp.typing import Envelope, Payload

# Push function typing alias
PushFunction = Union[Callable[..., Payload], Callable[..., Awaitable[Payload]]]


class PushExecutionError(Exception):
    """Is raised by push-plugins when the execution flow has failed."""


def enveloped(
    fun: PushFunction
) -> Callable[['Push', Payload], Payload]:
    """Decorator to split the envelope and the actual payload. This is an but a convenience
    decorator for `envelope_payload` of the `PushBase` class."""

    validator.is_function(fun=fun)

    def _call(self: 'Push', payload: Payload) -> Payload:
        validator.is_instance(Push, self=self)
        envelope, real_payload = self.envelope_payload(payload)
        return fun(
            self,
            envelope=envelope,
            payload=real_payload
        )

    if asyncio.iscoroutinefunction(fun):
        @functools.wraps(fun)
        async def _wrapper(self: 'Push', payload: Payload) -> Payload:
            return await _call(self, payload)
        return _wrapper

    return functools.wraps(fun)(_call)


def parse_envelope(value: str) -> PushFunction:
    """Decorator the parse the given value-key from the envelope. This is but a convenience
    decorator / wrapper for `_parse_envelope_value` of the `PushBase` class."""

    validator.is_instance(str, value=value)

    def _inner(fun: PushFunction) -> PushFunction:
        validator.is_function(fun=fun)

        def _call(
                self: 'Push', envelope: Optional[Envelope] = None, payload: Payload = None,
                **kwargs: Any
        ) -> Payload:
            validator.is_instance(Push, self=self)
            parsed = self._parse_envelope_value(value, envelope=envelope)

            new_kwargs = {
                value: parsed,
                'payload': payload
            }
            if envelope is not None:
                new_kwargs['envelope'] = envelope

            return fun(self, **{**new_kwargs, **kwargs})

        if asyncio.iscoroutinefunction(fun):
            @functools.wraps(fun)
            async def _wrapper(
                    self: 'Push', envelope: Optional[Envelope] = None, payload: Payload = None,
                    **kwargs: Any
            ) -> Payload:
                return await _call(self, envelope, payload, **kwargs)
            return _wrapper

        return functools.wraps(fun)(_call)
    return _inner


def drop_envelope(fun: PushFunction) -> PushFunction:
    """Decorator to drop the envelope from the arguments before calling the actual `push` method to
    make the linter happy again if necessary (unused-argument)."""

    def _call(self: 'Push', *args: Any, **kwargs: Any) -> Any:
        validator.is_instance(Push, self=self)
        kwargs.pop('envelope', None)
        return fun(self, *args, **kwargs)

    if asyncio.iscoroutinefunction(fun):
        @functools.wraps(fun)
        async def _wrapper(self: 'Push', *args: Any, **kwargs: Any) -> Any:
            return await _call(self, *args, **kwargs)
        return _wrapper

    return functools.wraps(fun)(_call)


def _lookup(instance: object, lookups: Union[str, Iterable[str]]) -> Optional[Any]:
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
        >>> _lookup(instance, 'a')
        1
        >>> _lookup(instance, '__a')
        99
        >>> _lookup(instance, ['c', 'b'])
        3
        >>> _lookup(instance, ['d', 'b'])
        2
        >>> print(_lookup(instance, ['x', 'y', 'z']))
        None

    Args:
        instance: The class to lookup for the given attribute names.
        lookups: Attribute names to lookup.

    Returns:
        Returns the value of the first found attribute name in lookups. If none is found, simply
        None is returned.
    """
    lookups = cast(List[str], utils.make_list(lookups) or [])
    # There might be some name mangling for private attributes - add them as lookups
    privates = ['_{classname}{attrname}'.format(classname=type(instance).__name__, attrname=x)
                for x in lookups if x.startswith('__') and not x.endswith('__')]
    lookups = lookups + privates
    _nothing = object()
    for lookup in lookups:
        val = getattr(instance, lookup, _nothing)
        if val is not _nothing:
            return val
    return None


class Push(Plugin):
    """Base class for all push plugins."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._assert_push_compat()

    def _assert_push_compat(self) -> None:
        self._assert_abstract_compat((SyncPush, AsyncPush))
        self._assert_fun_compat('_push')

    def _parse_envelope_value(
            self, name: str, envelope: Optional[Envelope] = None,
            parse_fun: Optional[Callable[[Any], Any]] = None,
            instance_lookup_fun: Optional[Callable[..., Optional[Any]]] = None
    ) -> Any:
        """
        Parse the envelope for the given `name`. If present in the envelope the extracted value will
        be tested / parsed by the given `parse_fun`. If no `parse_fun` is explicitly given, it will
        be determined if this instance provides a `parse_<name>`, `_parse_<name>` or a
        `__parse_<name>`. If yes the function is called; otherwise the value is returned as is.

        If the value is not present in the envelope the current instance will be probed for
        `<name>`, `_<name>` or `__<name>`. If an instance variable is present it will be returned
        unvalidated / unparsed (we assume that happened previously). If no variable is present
        simply `None` will be returned.

        Args:
            name: Name of the attribute to lookup in the envelope / instance.
            envelope: Envelope of the payload.
            parse_fun: Custom function to validate / parse. If not given it will be determined
                automagically.
            instance_lookup_fun: Custom function to perform instance variable lookups.
                If not given a reasonably default will be used.
        """
        validator.is_instance(str, name=name)
        validator.is_instance(dict, allow_none=True, envelope=envelope)
        if parse_fun:
            validator.is_function(parse_fun=parse_fun)
        if instance_lookup_fun:
            validator.is_function(instance_lookup_fun=instance_lookup_fun)

        lookups = cast(
            Dict[str, str], utils.make_public_protected_private_attr_lookup(name, as_dict=True)
        )

        if envelope is None or name not in envelope:
            return (
                instance_lookup_fun(name)
                if instance_lookup_fun is not None
                else _lookup(self, list(lookups.values()))  # pylint: disable=no-member
            )

        val = envelope[name]
        try:
            if parse_fun is None:
                public_attr_name = lookups['public']  # pylint: disable=invalid-sequence-index
                fun_base = 'parse_' + public_attr_name
                parse_fun_names = utils.make_public_protected_private_attr_lookup(fun_base)
                parse_fun = _lookup(self, parse_fun_names)
                if parse_fun is None:
                    return val
            return parse_fun(val)
        except (ValueError, TypeError):
            self.logger.exception(
                "Cannot parse value for '%s' from envelope",
                name
            )
            return (
                instance_lookup_fun(name)
                if instance_lookup_fun is not None
                else _lookup(self, list(lookups.values()))  # pylint: disable=no-member
            )

    @staticmethod
    def envelope_payload(payload: Payload) -> Tuple[Envelope, Payload]:
        """
        A payload might be enveloped (but actually it even may not). The actual payload will be
        available via data or payload inside the dictionary. All other keys are the envelope.

        Args:
            payload: Payload (which might be enveloped or not).

        Returns:
            A tuple consisting of envelope (might be None) and the real payload.

        Examples:

            >>> SyncPush.envelope_payload(1234)  # No envelope -> payload as is
            ({}, 1234)
            >>> (SyncPush.envelope_payload({'key1': 'val1', 'key2': 'val2'}) ==
            ...     ({}, {'key1': 'val1', 'key2': 'val2'}))
            True
            >>> SyncPush.envelope_payload({'data': 1234})  # Envelope with the data key only
            ({}, 1234)
            >>> SyncPush.envelope_payload({'payload': 1234})  # Works with 'payload' as well
            ({}, 1234)
            >>> SyncPush.envelope_payload({'envelope1': 'envelope', 'payload': 1234})
            ({'envelope1': 'envelope'}, 1234)
        """
        payload = copy.deepcopy(payload)

        if not isinstance(payload, dict):
            return {}, payload

        if 'data' in payload:
            real_payload = payload.pop('data')
        elif 'payload' in payload:
            real_payload = payload.pop('payload')
        else:
            return {}, payload  # There is no envelope

        # We popped the real payload -> all what is left in payload is the envelope
        return payload, real_payload

    async def push(self, payload: Payload) -> Payload:
        """Transforms the payload and/or pushes it to a sink."""
        push_fun = getattr(self, '_push')
        if inspect.iscoroutinefunction(push_fun):
            return await push_fun(payload)
        return await run_sync(push_fun, payload)


class SyncPush(Push):
    """Base class for all synchronous push plugins."""

    @abstractmethod
    def _push(self, payload: Payload) -> Payload:
        """
        This is where the hard work happens.

        Args:
            payload: The payload.
        """
        raise NotImplementedError()  # pragma: no cover


class AsyncPush(Push):
    """Base class for all asynchronous push plugins."""

    @abstractmethod
    async def _push(self, payload: Payload) -> Payload:
        """
        This is where the hard work happens.

        Args:
            payload: The payload.
        """
        raise NotImplementedError()  # pragma: no cover
