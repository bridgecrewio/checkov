# -*- coding: utf-8 -*-
"""
=================
stopit.signalstop
=================

Control the timeout of blocks or callables with a context manager or a
decorator. Based on the use of signal.SIGALRM
"""

import signal

from .utils import TimeoutException, BaseTimeout, base_timeoutable


class SignalTimeout(BaseTimeout):
    """Context manager for limiting in the time the execution of a block
    using signal.SIGALRM Unix signal.

    See :class:`stopit.utils.BaseTimeout` for more information
    """
    def __init__(self, seconds, swallow_exc=True):
        seconds = int(seconds)  # alarm delay for signal MUST be int
        super(SignalTimeout, self).__init__(seconds, swallow_exc)

    def handle_timeout(self, signum, frame):
        self.state = BaseTimeout.TIMED_OUT
        raise TimeoutException('Block exceeded maximum timeout '
                               'value (%d seconds).' % self.seconds)

    # Required overrides
    def setup_interrupt(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def suppress_interrupt(self):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)


class signal_timeoutable(base_timeoutable):  #noqa
    """A function or method decorator that raises a ``TimeoutException`` to
    decorated functions that should not last a certain amount of time.
    this one uses ``SignalTimeout`` context manager.

    See :class:`.utils.base_timoutable`` class for further comments.
    """
    to_ctx_mgr = SignalTimeout
