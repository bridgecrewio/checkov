# -*- coding: utf-8 -*-
"""
=================
stopit.signalstop
=================

Control the timeout of blocks or callables with a context manager or a
decorator. Based on the use of signal.SIGALRM
"""

from __future__ import annotations

import signal
from typing import TYPE_CHECKING

from .utils import TimeoutException, BaseTimeout, base_timeoutable

if TYPE_CHECKING:
    from types import FrameType


class SignalTimeout(BaseTimeout):
    """Context manager for limiting in the time the execution of a block
    using signal.SIGALRM Unix signal.

    See :class:`stopit.utils.BaseTimeout` for more information
    """

    def __init__(self, seconds: int, swallow_exc: bool = True) -> None:
        seconds = int(seconds)  # alarm delay for signal MUST be int
        super().__init__(seconds, swallow_exc)

    def handle_timeout(self, signum: int, frame: FrameType | None) -> None:
        self.state = self.TIMED_OUT
        raise TimeoutException(f"Block exceeded maximum timeout value ({self.seconds} seconds).")

    # Required overrides
    def setup_interrupt(self) -> None:
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def suppress_interrupt(self) -> None:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)


class signal_timeoutable(base_timeoutable):  # noqa: B903
    """A function or method decorator that raises a ``TimeoutException`` to
    decorated functions that should not last a certain amount of time.
    this one uses ``SignalTimeout`` context manager.

    See :class:`.utils.base_timoutable`` class for further comments.
    """
    def __init__(self) -> None:
        super().__init__()
        self.to_ctx_mgr = SignalTimeout
