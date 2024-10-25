from __future__ import annotations

from typing import Any


def extract_commands(conf: dict[str, Any]) -> tuple[list[str], list[str]]:
    commands = conf.get("command")
    if not commands or not isinstance(commands, list):
        return [], []
    values = []
    keys = []
    for cmd in commands:
        if cmd is None:
            continue
        if isinstance(cmd, str) and "=" in cmd:
            key, value = cmd.split("=", maxsplit=1)
            keys.append(key)
            values.append(value)
        else:
            keys.append(cmd)
            values.append('')
    return keys, values
