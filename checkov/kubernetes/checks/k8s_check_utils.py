from typing import List


def extract_commands(conf: dict) -> (List[str], List[str]):
    commands: List[str] = conf.get("command")
    if not commands:
        return [], []
    values = []
    keys = []
    for cmd in commands:
        if cmd is None:
            continue
        if "=" in cmd:
            firstEqual = cmd.index("=")
            [key, value] = [cmd[:firstEqual], cmd[firstEqual + 1:]]
            keys.append(key)
            values.append(value)
        else:
            keys.append(cmd)
            values.append(None)
    return keys, values
