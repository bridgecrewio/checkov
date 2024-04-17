import re

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
seconds_per_unit_regex = r"^\d+[s|m|h|d|w]"


# method 'str.removeprefix()' was added in Python 3.9
def removeprefix(input_str: str, prefix: str) -> str:
    if input_str.startswith(prefix):
        return input_str[len(prefix):]
    return input_str


def convert_to_seconds(input_str: str) -> int:
    if re.search(seconds_per_unit_regex, input_str) is None:
        raise Exception(f"format error for input str, usage: {seconds_per_unit_regex}")
    return int(input_str[:-1]) * seconds_per_unit[input_str[-1]]
