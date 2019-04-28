"""Publishing engine classes to the outside world."""

from .async_ import AsyncEngine
from .thread import ThreadEngine
from .process import ProcessEngine
from .sequential import SequentialEngine

from .base import (Engine, RetryDirective, RetryHandler, NoRetryHandler, SimpleRetryHandler,
                   LimitedRetryHandler, AdvancedRetryHandler, PushExecutor, NotSupportedError)


DEFAULT_ENGINES = {
    'async': AsyncEngine(retry_handler=AdvancedRetryHandler()),
    'process': ProcessEngine(queue_worker=3, retry_handler=AdvancedRetryHandler()),
    'thread': ThreadEngine(queue_worker=3, retry_handler=AdvancedRetryHandler()),
    'sequential': SequentialEngine(retry_handler=AdvancedRetryHandler())
}


__all__ = ['Engine', 'AsyncEngine', 'ProcessEngine', 'SequentialEngine', 'ThreadEngine',
           'RetryDirective', 'RetryHandler', 'NoRetryHandler', 'SimpleRetryHandler',
           'LimitedRetryHandler', 'AdvancedRetryHandler', 'PushExecutor', 'NotSupportedError',
           'DEFAULT_ENGINES']
