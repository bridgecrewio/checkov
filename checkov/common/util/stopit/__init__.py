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

import pkg_resources

from .utils import LOG, TimeoutException
from .threadstop import ThreadingTimeout, async_raise, threading_timeoutable
from .signalstop import SignalTimeout, signal_timeoutable

# PEP 396 style version marker
try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    LOG.warning("Could not get the package version from pkg_resources")
    __version__ = 'unknown'

__all__ = (
    'ThreadingTimeout', 'async_raise', 'threading_timeoutable',
    'SignalTimeout', 'signal_timeoutable'
)
