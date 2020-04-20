"""Publishing engine classes to the outside world."""

from ._async import AsyncEngine
from ._base import (
    Engine,
    RetryDirective,
    RetryHandler,
    NoRetryHandler,
    SimpleRetryHandler,
    LimitedRetryHandler,
    AdvancedRetryHandler,
    PushExecutor,
    NotSupportedError
)


DEFAULT_ENGINES = {
    'async': lambda: AsyncEngine(retry_handler=AdvancedRetryHandler()),
}


__all__ = [
    'Engine', 'AsyncEngine', 'RetryDirective', 'RetryHandler', 'NoRetryHandler',
    'SimpleRetryHandler', 'LimitedRetryHandler', 'AdvancedRetryHandler', 'PushExecutor',
    'NotSupportedError', 'DEFAULT_ENGINES']
