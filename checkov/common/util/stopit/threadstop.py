# -*- coding: utf-8 -*-
"""
=================
stopit.threadstop
=================

Raise asynchronous exceptions in other thread, control the timeout of blocks
or callables with a context manager or a decorator.
"""

from __future__ import annotations

import ctypes
import threading

from .utils import TimeoutException, BaseTimeout, base_timeoutable


def async_raise(target_tid: int, exception: type[Exception]) -> None:
    """Raises an asynchronous exception in another thread.
    Read http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
    for further enlightenments.

    :param target_tid: target thread identifier
    :param exception: Exception class to be raised in that thread
    """
    # Ensuring and releasing GIL are useless since we're not in C
    # gil_state = ctypes.pythonapi.PyGILState_Ensure()
    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid),
                                                     ctypes.py_object(exception))
    # ctypes.pythonapi.PyGILState_Release(gil_state)
    if ret == 0:
        raise ValueError(f"Invalid thread ID {target_tid}")
    elif ret > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class ThreadingTimeout(BaseTimeout):
    """Context manager for limiting in the time the execution of a block
    using asynchronous threads launching exception.

    See :class:`stopit.utils.BaseTimeout` for more information
    """
    def __init__(self, seconds: int, swallow_exc: bool = True) -> None:
        super().__init__(seconds, swallow_exc)
        self.target_tid = threading.current_thread().ident
        self.timer: "threading.Timer | None" = None  # PEP8

    def stop(self) -> None:
        """Called by timer thread at timeout. Raises a Timeout exception in the
        caller thread
        """
        self.state = self.TIMED_OUT
        if self.target_tid is not None:
            async_raise(self.target_tid, TimeoutException)

    # Required overrides
    def setup_interrupt(self) -> None:
        """Setting up the resource that interrupts the block
        """
        self.timer = threading.Timer(self.seconds, self.stop)
        self.timer.start()

    def suppress_interrupt(self) -> None:
        """Removing the resource that interrupts the block
        """
        if self.timer:
            self.timer.cancel()


class threading_timeoutable(base_timeoutable):  # noqa: B903
    """A function or method decorator that raises a ``TimeoutException`` to
    decorated functions that should not last a certain amount of time.
    this one uses ``ThreadingTimeout`` context manager.

    See :class:`.utils.base_timoutable`` class for further comments.
    """
    def __init__(self) -> None:
        super().__init__()
        self.to_ctx_mgr = ThreadingTimeout
