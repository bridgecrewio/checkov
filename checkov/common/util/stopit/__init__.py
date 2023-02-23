# -*- coding: utf-8 -*-
"""
======
stopit
======

code from:
https://github.com/glenfant/stopit
package:
https://pypi.org/project/stopit

Public resources from ``stopit``
"""

from .utils import TimeoutException
from .threadstop import ThreadingTimeout, async_raise, threading_timeoutable
from .signalstop import SignalTimeout, signal_timeoutable


__all__ = (
    'ThreadingTimeout', 'async_raise', 'threading_timeoutable',
    'SignalTimeout', 'signal_timeoutable', 'TimeoutException'
)
