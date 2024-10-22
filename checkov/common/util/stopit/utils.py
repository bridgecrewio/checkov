# -*- coding: utf-8 -*-
"""
============
stopit.utils
============

Misc utilities and common resources
"""

from __future__ import annotations

import functools
import logging
from logging import NullHandler
from typing import TYPE_CHECKING, Any, TypeVar, Callable, cast

from typing_extensions import ParamSpec, Self

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger

if TYPE_CHECKING:
    from types import TracebackType

T = TypeVar("T")
P = ParamSpec("P")

# Custom logger
LOG = logging.getLogger(name='stopit')
LOG.addHandler(NullHandler())
add_resource_code_filter_to_logger(LOG)


class TimeoutException(Exception):
    """Raised when the block under context management takes longer to complete
    than the allowed maximum timeout value.
    """
    pass


class BaseTimeout:
    """Context manager for limiting in the time the execution of a block

    :param seconds: ``float`` or ``int`` duration enabled to run the context
      manager block
    :param swallow_exc: ``False`` if you want to manage the
      ``TimeoutException`` (or any other) in an outer ``try ... except``
      structure. ``True`` (default) if you just want to check the execution of
      the block with the ``state`` attribute of the context manager.
    """

    def __init__(self, seconds: int, swallow_exc: bool = True) -> None:

        # Possible values for the ``state`` attribute, self explanative
        self.EXECUTED, self.EXECUTING, self.TIMED_OUT, self.INTERRUPTED, self.CANCELED = range(5)

        self.seconds = seconds
        self.swallow_exc = swallow_exc
        self.state = self.EXECUTED

    def __bool__(self) -> bool:
        return self.state in (self.EXECUTED, self.EXECUTING, self.CANCELED)

    def __repr__(self) -> str:
        """Debug helper
        """
        return f"<{self.__class__.__name__} in state: {self.state}>"

    def __enter__(self) -> Self:
        self.state = self.EXECUTING
        self.setup_interrupt()
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType | None) -> bool:
        if exc_type is TimeoutException:
            if self.state != self.TIMED_OUT:
                self.state = self.INTERRUPTED
                self.suppress_interrupt()
            LOG.warning(
                f"Code block execution exceeded {self.seconds} seconds timeout",
                exc_info=(exc_type, exc_val, exc_tb),
            )
            return self.swallow_exc
        else:
            if exc_type is None:
                self.state = self.EXECUTED
            self.suppress_interrupt()
        return False

    def cancel(self) -> None:
        """In case in the block you realize you don't need anymore
       limitation"""
        self.state = self.CANCELED
        self.suppress_interrupt()

    # Methods must be provided by subclasses
    def suppress_interrupt(self) -> None:
        """Removes/neutralizes the feature that interrupts the executed block
        """
        raise NotImplementedError

    def setup_interrupt(self) -> None:
        """Installs/initializes the feature that interrupts the executed block
        """
        raise NotImplementedError


class base_timeoutable:
    """A base for function or method decorator that raises a ``TimeoutException`` to
    decorated functions that should not last a certain amount of time.

    Any decorated callable may receive a ``timeout`` optional parameter that
    specifies the number of seconds allocated to the callable execution.

    The decorated functions that exceed that timeout return ``None`` or the
    value provided by the decorator.

    :param default: The default value in case we timed out during the decorated
      function execution. Default is None.

    :param timeout_param: As adding dynamically a ``timeout`` named parameter
      to the decorated callable may conflict with the callable signature, you
      may choose another name to provide that parameter. Your decoration line
      could look like ``@timeoutable(timeout_param='my_timeout')``

    .. note::

       This is a base class that must be subclassed. subclasses must override
       thz ``to_ctx_mgr`` with a timeout  context manager class which in turn
       must subclasses of above ``BaseTimeout`` class.
    """

    def __init__(self, default: Any = None, timeout_param: str = 'timeout') -> None:
        self.to_ctx_mgr: "type[BaseTimeout] | None" = None
        self.default, self.timeout_param = default, timeout_param

    def __call__(self, func: Callable[P, T]) -> Callable[P, T | Any]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | Any:
            timeout = cast(int, kwargs.pop(self.timeout_param, 0))
            if timeout:
                if not self.to_ctx_mgr:
                    return self.default

                with self.to_ctx_mgr(timeout, swallow_exc=True):
                    result = self.default
                    # ``result`` may not be assigned below in case of timeout
                    result = func(*args, **kwargs)
                return result
            else:
                return func(*args, **kwargs)
        return wrapper
