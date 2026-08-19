import platform
import re
from pathlib import PureWindowsPath

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
seconds_per_unit_regex = r"^\d+[s|m|h|d|w]"

IS_WINDOWS = platform.system() == "Windows"


# method 'str.removeprefix()' was added in Python 3.9
def removeprefix(input_str: str, prefix: str) -> str:
    if input_str.startswith(prefix):
        return input_str[len(prefix):]
    return input_str


# in case of comparing paths from the BE and from the client, we have to make sure the structures are the same
# e.g: in windows the separator for the path is '\' while in linux/max it is '/'
def align_path(path: str) -> str:
    return path.replace('\\', '/')


def get_rootless_path(path: str) -> str:
    """Strip a leading drive, UNC share or root prefix from a Windows path.

    Only for use on Windows -- guard calls with ``IS_WINDOWS``. On POSIX a leading '//'
    is a valid root, which Windows semantics would misread as a UNC share.

    Replaces ``path.replace(Path(path).anchor, "", 1)``, which is not positionally
    aware: for a mixed-separator path like ``/repo\\client\\Dockerfile`` the anchor is a
    bare ``'\\'``, so ``str.replace`` removes the first separator anywhere in the string
    and yields ``/repoclient\\Dockerfile``.

    Separators are left as-is; use ``align_path()`` for a platform-independent form.
    """
    win_anchor = PureWindowsPath(path).anchor
    if win_anchor not in ('', '\\', '/'):  # a real drive (C:\) or UNC (\\srv\share\)
        path = path[len(win_anchor):]
    return path.lstrip('\\/')


def convert_to_seconds(input_str: str) -> int:
    if re.search(seconds_per_unit_regex, input_str) is None:
        raise Exception(f"format error for input str, usage: {seconds_per_unit_regex}")
    return int(input_str[:-1]) * seconds_per_unit[input_str[-1]]
