"""Publishing engine classes to the outside world."""

from .async_ import AsyncEngine
from .thread import ThreadEngine
from .process import ProcessEngine
from .sequential import SequentialEngine

from .base import (Engine, RetryDirective, RetryHandler, NoRetryHandler, SimpleRetryHandler,
                   LimitedRetryHandler, AdvancedRetryHandler, PushExecutor, NotSupportedError)


DEFAULT_ENGINES = {
    'async': lambda: AsyncEngine(retry_handler=AdvancedRetryHandler()),
    'process': lambda: ProcessEngine(queue_worker=3, retry_handler=AdvancedRetryHandler()),
    'sequential': lambda: SequentialEngine(retry_handler=NoRetryHandler()),
    'thread': lambda: ThreadEngine(queue_worker=3, retry_handler=AdvancedRetryHandler())
}


__all__ = ['Engine', 'AsyncEngine', 'ProcessEngine', 'SequentialEngine', 'ThreadEngine',
           'RetryDirective', 'RetryHandler', 'NoRetryHandler', 'SimpleRetryHandler',
           'LimitedRetryHandler', 'AdvancedRetryHandler', 'PushExecutor', 'NotSupportedError',
           'DEFAULT_ENGINES']
