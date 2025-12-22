from __future__ import annotations

import sys
from io import StringIO
import pytest

_REAL_STDERR = sys.stderr
_STDERR_BUFFER = StringIO()

def pytest_configure():
    sys.stderr = _STDERR_BUFFER


def pytest_sessionfinish(session, exitstatus):
    sys.stderr = _REAL_STDERR

    out = _STDERR_BUFFER.getvalue()
    if not out:
        return

    MAX = 1000 

    if len(out) > MAX:
        out = out[:MAX] + "\n... [stderr truncated]"

    _REAL_STDERR.write(out)
