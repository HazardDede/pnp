"""Contains envelope decorator utility functions."""

import asyncio
import functools
from typing import Callable, Awaitable, Union, Any, Optional

from pnp import validator
from pnp.plugins.push import Push
from pnp.typing import Payload, Envelope as EnvelopeType

PushFunctionResult = Union[Payload, Awaitable[Payload]]
PushFunction = Callable[[Push, Payload], PushFunctionResult]
PushUnwrappedFunction = Callable[..., PushFunctionResult]


class Envelope:
    """Class to group envelope convenient/helper decorators together."""

    @staticmethod
    def unwrap(fun: PushUnwrappedFunction) -> PushFunction:
        """Decorator to split the envelope and the actual payload. This is an but a convenience
        decorator for `envelope_payload` of the `PushBase` class."""

        validator.is_function(fun=fun)

        def _call(self: Push, payload: Payload) -> PushFunctionResult:
            validator.is_instance(Push, self=self)
            envelope, real_payload = self.envelope_payload(payload)
            # Reminder: The result might be an awaitable as well!
            return fun(
                self,
                envelope=envelope,
                payload=real_payload
            )

        if not asyncio.iscoroutinefunction(fun):
            return functools.wraps(fun)(_call)  # Target is not a coroutine. We are done!

        @functools.wraps(fun)
        async def _wrapper(self: Push, payload: Payload) -> Payload:
            return await _call(self, payload)
        return _wrapper

    @staticmethod
    def parse(value: str) -> Callable[[PushUnwrappedFunction], PushUnwrappedFunction]:
        """Decorator to parse the given value-key from the envelope. This is a a convenience
        decorator / wrapper for `_parse_envelope_value` of the `Push` class."""

        value = str(value)

        def _inner(fun: PushUnwrappedFunction) -> PushUnwrappedFunction:
            def _call(
                    self: Push,
                    envelope: Optional[EnvelopeType] = None,
                    payload: Payload = None,
                    **kwargs: Any
            ) -> PushFunctionResult:
                validator.is_instance(Push, self=self)
                # pylint: disable=protected-access
                parsed = self._parse_envelope_value(value, envelope=envelope)

                new_kwargs = {
                    **kwargs,
                    value: parsed,
                    'payload': payload
                }
                if envelope is not None:
                    new_kwargs['envelope'] = envelope

                return fun(self, **new_kwargs)

            if not asyncio.iscoroutinefunction(fun):
                return functools.wraps(fun)(_call)

            @functools.wraps(fun)
            async def _wrapper(
                    self: 'Push',
                    envelope: Optional[EnvelopeType] = None,
                    payload: Payload = None,
                    **kwargs: Any
            ) -> Payload:
                return await _call(self, envelope, payload, **kwargs)

            return _wrapper
        return _inner

    @staticmethod
    def drop(fun: PushUnwrappedFunction) -> PushUnwrappedFunction:
        """Decorator to drop the envelope from the arguments before calling the actual `push`
        method."""

        def _call(self: Push, *args: Any, **kwargs: Any) -> PushFunctionResult:
            validator.is_instance(Push, self=self)
            kwargs.pop('envelope', None)
            return fun(self, *args, **kwargs)

        if not asyncio.iscoroutinefunction(fun):
            return functools.wraps(fun)(_call)

        @functools.wraps(fun)
        async def _wrapper(self: Push, *args: Any, **kwargs: Any) -> Payload:
            return await _call(self, *args, **kwargs)
        return _wrapper
