# -*- coding: utf-8 -*-
"""
============
stopit.utils
============

Misc utilities and common resources
"""

import functools
import logging
import sys

# Custom logger
LOG = logging.getLogger(name='stopit')

if sys.version_info < (2, 7):
    class NullHandler(logging.Handler):
        """Copied from Python 2.7 to avoid getting `No handlers could be found
        for logger "xxx"` http://bugs.python.org/issue16539
        """
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None  # noqa
else:
    from logging import NullHandler

LOG.addHandler(NullHandler())


class TimeoutException(Exception):
    """Raised when the block under context management takes longer to complete
    than the allowed maximum timeout value.
    """
    pass


class BaseTimeout(object):
    """Context manager for limiting in the time the execution of a block

    :param seconds: ``float`` or ``int`` duration enabled to run the context
      manager block
    :param swallow_exc: ``False`` if you want to manage the
      ``TimeoutException`` (or any other) in an outer ``try ... except``
      structure. ``True`` (default) if you just want to check the execution of
      the block with the ``state`` attribute of the context manager.
    """
    # Possible values for the ``state`` attribute, self explanative
    EXECUTED, EXECUTING, TIMED_OUT, INTERRUPTED, CANCELED = range(5)

    def __init__(self, seconds, swallow_exc=True):
        self.seconds = seconds
        self.swallow_exc = swallow_exc
        self.state = BaseTimeout.EXECUTED

    def __bool__(self):
        return self.state in (BaseTimeout.EXECUTED, BaseTimeout.EXECUTING, BaseTimeout.CANCELED)

    __nonzero__ = __bool__  # Python 2.x

    def __repr__(self):
        """Debug helper
        """
        return "<{0} in state: {1}>".format(self.__class__.__name__, self.state)

    def __enter__(self):
        self.state = BaseTimeout.EXECUTING
        self.setup_interrupt()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is TimeoutException:
            if self.state != BaseTimeout.TIMED_OUT:
                self.state = BaseTimeout.INTERRUPTED
                self.suppress_interrupt()
            LOG.warning("Code block execution exceeded {0} seconds timeout".format(self.seconds),
                        exc_info=(exc_type, exc_val, exc_tb))
            return self.swallow_exc
        else:
            if exc_type is None:
                self.state = BaseTimeout.EXECUTED
            self.suppress_interrupt()
        return False

    def cancel(self):
        """In case in the block you realize you don't need anymore
       limitation"""
        self.state = BaseTimeout.CANCELED
        self.suppress_interrupt()

    # Methods must be provided by subclasses
    def suppress_interrupt(self):
        """Removes/neutralizes the feature that interrupts the executed block
        """
        raise NotImplementedError

    def setup_interrupt(self):
        """Installs/initializes the feature that interrupts the executed block
        """
        raise NotImplementedError


class base_timeoutable(object):  # noqa
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
    to_ctx_mgr = None

    def __init__(self, default=None, timeout_param='timeout'):
        self.default, self.timeout_param = default, timeout_param

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timeout = kwargs.pop(self.timeout_param, None)
            if timeout:
                with self.to_ctx_mgr(timeout, swallow_exc=True):
                    result = self.default  # noqa
                    # ``result`` may not be assigned below in case of timeout
                    result = func(*args, **kwargs)
                return result
            else:
                return func(*args, **kwargs)
        return wrapper
