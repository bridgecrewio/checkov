from __future__ import annotations

import itertools
import logging
import os
import re
from datetime import datetime, timedelta
from functools import reduce
from math import ceil, floor, log
from typing import Union, Any, Dict, Callable, List, Optional
from asteval import Interpreter

from checkov.terraform.parser_functions import tonumber, FUNCTION_FAILED, create_map, tobool, tostring

TIME_DELTA_PATTERN = re.compile(r"(\d*\.*\d+)")
RANGE_PATTERN = re.compile(r'^\d+-\d+$')

"""
This file contains a custom implementation of the builtin `eval` function.
`eval` is not a safe function, because it can execute *every* command,
so this file overrides `eval` and allows only the functions in SAFE_EVAL_DICT.

The functions are an implementation of Terraform's built-in functions
https://www.terraform.io/docs/configuration/functions.html

Not all of the functions are implemented yet. If a function doesn't exist, the original value is returned.
"""


def _find_regex_groups(pattern: str, input_str: str) -> Optional[Union[Dict[str, str], List[str]]]:
    match = re.match(pattern, input_str)
    if match:
        if match.groupdict():
            # try to find named capturing groups
            return match.groupdict()
        if list(match.groups()):
            # try to find unnamed capturing groups
            return list(match.groups())
    return None


def regex(pattern: str, input_str: str) -> Union[Dict[str, str], List[str], str]:
    try:
        groups = _find_regex_groups(pattern, input_str)
        if groups is not None:
            return groups

        results: List[str] = re.findall(pattern, input_str)
        # return first match
        if len(results) > 0:
            return results[0]
        return ""
    except TypeError:
        return f"regex({pattern}, {input_str})"


def regexall(pattern: str, input_str: str) -> Union[Dict[str, str], List[str], str]:
    try:
        groups = _find_regex_groups(pattern, input_str)
        if groups is not None:
            return groups

        results = re.findall(pattern, input_str)
        return results
    except TypeError:
        return f"regexall({pattern}, {input_str})"


def trim(input_str: str, chars_to_remove: str) -> str:
    for c in chars_to_remove:
        input_str = input_str.replace(c, "")
    return input_str


def coalesce(*arg: Any) -> Any:
    return reduce(lambda x, y: x if x not in [None, ""] else y, arg)


def coalesce_list(*arg: List[Any]) -> List[Any]:
    return reduce(lambda x, y: x if x not in [None, []] else y, arg)


def flatten(lst: List[List[Any]]) -> List[Any]:
    res = [item for sublist in lst for item in sublist]
    if any(type(elem) is list for elem in res):
        return flatten(res)
    else:
        return res


def matchkeys(values_list: List[Any], keys_list: List[Any], search_set: List[Any]) -> List[Any]:
    matching = set()
    for search in search_set:
        indices = [i for i, x in enumerate(keys_list) if x == search]
        for i in indices:
            matching.add(values_list[i])

    return list(matching)


def reverse(lst: List[Any]) -> List[Any]:
    lst.reverse()
    return lst


def sort(lst: List[str]) -> List[str]:
    lst.sort()
    return lst


def merge(*args: Any) -> Dict[str, Any]:
    res: Dict[str, Any] = {}
    for d in args:
        res = {**res, **d}
    return res


def wrap_func(f: Callable[..., Any], *args: Any) -> Any:
    res = f(*args)
    if res == FUNCTION_FAILED:
        raise ValueError
    return res


def update_datetime(dt: datetime, delta: timedelta, adding: bool) -> datetime:
    if adding is True:
        dt = dt + delta
    else:
        dt = dt - delta
    return dt


def timeadd(input_str: str, time_delta: str) -> str:
    '''
    From docs:
    duration is a string representation of a time difference, consisting of sequences of number and unit pairs,
     like "1.5h" or "1h30m". The accepted units are "ns", "us" (or "µs"), "ms", "s", "m", and "h".
     The first number may be negative to indicate a negative duration, like "-2h5m".
    '''

    # Convert the date to allowing parsing
    input_str = input_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(input_str)
    adding = True
    if time_delta[0] == '-':
        adding = False
        time_delta = time_delta[1:]
    # Split out into each of the deltas
    deltas = re.split(TIME_DELTA_PATTERN, time_delta)
    # Needed to strip the leading empty element
    deltas = list(filter(None, deltas))
    while len(deltas) > 0:
        amount = float(deltas[0])
        interval = deltas[1]
        deltas = deltas[2:]
        delta = timedelta(0)
        if interval == 'h':
            delta = timedelta(hours=amount)
        elif interval == 'm':
            delta = timedelta(minutes=amount)
        elif interval == 's':
            delta = timedelta(seconds=amount)
        elif interval == 'ms':
            delta = timedelta(milliseconds=amount)
        elif interval == 'us' or interval == 'µs':
            delta = timedelta(microseconds=amount)
        elif interval == 'ns':  # Crude, but timedelta does not deal with nanoseconds
            delta = timedelta(microseconds=(amount / 1000))

        dt = update_datetime(dt, delta, adding)

    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def process_formatting_codes(format_str: str, dt: datetime) -> str:
    format_mapping = {
        "YYYY": "%Y",
        "YY": "%y",
        "MMMM": "%B",
        "MMM": "%b",
        "MM": "%m",
        "M": "%-m",
        "DD" : "%d",
        "D" : "%-d",
        "EEEE" : "%A",
        "EEE" : "%a",
        "HH" : "%I",
        "H" : "%-I",
        "hh" : "%H",
        "h" : "%-H",
        "mm" : "%M",
        "m" : "%-M",
        "ss" : "%S",
        "s" : "%-S",
        "AA" : "%p",
        # "aa" : "%p",  # included for completeness but requires separate handling
        "ZZZZZ" : "%z",
        "ZZZZ" : "%z",
        "ZZZ" : "%z",
        "Z " : "%z"}

    if format_str == 'aa':
        format_str = dt.strftime('%p').lower()
    elif format_str == 'ZZZZZ':
        tz = dt.strftime("%z")
        format_str = tz[:3] + ":" + tz[3:]
    elif format_str == 'ZZZ':
        tz = dt.strftime("%z")
        if tz == '+0000':
            tz = 'UTC'
        format_str = tz
    elif format_str == 'Z':
        tz = dt.strftime("%z")
        if tz == '+0000':
            tz = 'Z'
        format_str = tz
    else:
        format_str = format_mapping.get(format_str, format_str)

    return format_str


def formatdate(format_str: str, input_str: str) -> str:
    '''
    From docs: This function is intended for producing common machine-oriented timestamp formats such as
    those defined in RFC822, RFC850, and RFC1123. It is not suitable for truly human-oriented date
    formatting because it is not locale-aware.
    Any non-letter characters, such as punctuation, are reproduced verbatim in the output.
    To include literal letters in the format string, enclose them in single quotes '.
    To include a literal quote, escape it by doubling the quotes.
    Function works through the format string halting on single quotes to process any formatting
    '''

    # Convert the input str to a date
    input_str = input_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(input_str)

    processed_format_str = ""
    format_str_segment = ""
    in_quote = False  # Keep track of whether in formatting or quoted text
    last_ch = ""  # Used to identify the '' scenario
    for ch in format_str:
        if ch == "'" or in_quote is True:
            if len(format_str_segment) > 0:
                processed_format_str += process_formatting_codes(format_str_segment, dt)
                format_str_segment = ""
            if ch == "'":
                if last_ch == "'":
                    processed_format_str += "'"
                in_quote = not in_quote
            else:
                processed_format_str += ch
        else:
            if ch != last_ch and last_ch != "":  # new format code and the start of the string
                processed_format_str += process_formatting_codes(format_str_segment, dt)
                format_str_segment = ""
            format_str_segment += ch
        last_ch = ch
    if len(format_str_segment) > 0:
        processed_format_str += process_formatting_codes(format_str_segment, dt)

    return dt.strftime(processed_format_str)


def terraform_try(*args: Any) -> Any:
    """
    From terraform docs:
        "try evaluates all of its argument expressions in turn and returns the result of the first one that does not
        produce any errors."
    """
    for arg in args:
        try:
            return evaluate(arg) if isinstance(arg, str) else arg
        except Exception as e:
            logging.warning(f"Error in evaluate_try of argument {arg} - {e}")
            continue
    raise Exception(f"No argument can be evaluated for try of {args}")


SAFE_EVAL_FUNCTIONS: List[str] = []
SAFE_EVAL_DICT = dict([(k, locals().get(k, None)) for k in SAFE_EVAL_FUNCTIONS])


# type conversion functions
TRY_STR_REPLACEMENT = "__terraform_try__"
SAFE_EVAL_DICT[TRY_STR_REPLACEMENT] = terraform_try

# math functions
SAFE_EVAL_DICT["abs"] = abs
SAFE_EVAL_DICT["ceil"] = ceil
SAFE_EVAL_DICT["floor"] = floor
SAFE_EVAL_DICT["log"] = log
SAFE_EVAL_DICT["max"] = max
SAFE_EVAL_DICT["min"] = min
SAFE_EVAL_DICT["parsint"] = int
SAFE_EVAL_DICT["pow"] = pow
SAFE_EVAL_DICT["signum"] = lambda x: -1 if x < 0 else 0 if x == 0 else 1

# string functions
SAFE_EVAL_DICT["chomp"] = lambda x: x.rstrip()
SAFE_EVAL_DICT["format"] = lambda text_to_format, *args: (text_to_format % args)
SAFE_EVAL_DICT["formatlist"] = lambda text_to_format, args_list: [(text_to_format % args) for args in args_list]
SAFE_EVAL_DICT["indent"] = lambda num_of_space, input_str: input_str
SAFE_EVAL_DICT["join"] = lambda separator, lst: separator.join(lst)
SAFE_EVAL_DICT["lower"] = lambda input_str: input_str.lower()
SAFE_EVAL_DICT["regex"] = regex
SAFE_EVAL_DICT["regexall"] = regexall
SAFE_EVAL_DICT["replace"] = lambda string, substring, replacement: string.replace(substring, replacement)
SAFE_EVAL_DICT["split"] = lambda separator, input_str: input_str.split(separator)
SAFE_EVAL_DICT["strrev"] = lambda input_str: input_str[::-1]
SAFE_EVAL_DICT["substr"] = lambda input_str, offset, length: input_str[offset : offset + length]
SAFE_EVAL_DICT["title"] = lambda input_str: input_str.title()
SAFE_EVAL_DICT["trim"] = trim
SAFE_EVAL_DICT["trimprefix"] = lambda input_str, prefix: input_str.lstrip(prefix)
SAFE_EVAL_DICT["trimsuffix"] = lambda input_str, prefix: input_str.rstrip(prefix)
SAFE_EVAL_DICT["trimspace"] = lambda input_str: input_str.strip()
SAFE_EVAL_DICT["upper"] = lambda input_str: input_str.upper()

# collections
SAFE_EVAL_DICT["chunklist"] = lambda lst, chunk_size: [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
SAFE_EVAL_DICT["coalesce"] = coalesce
SAFE_EVAL_DICT["coalescelist"] = coalesce_list
SAFE_EVAL_DICT["compact"] = lambda lst: list(filter(lambda value: value != "", lst))
SAFE_EVAL_DICT["concat"] = lambda *lists: list(itertools.chain(*lists))
SAFE_EVAL_DICT["contains"] = lambda lst, value: value in lst
SAFE_EVAL_DICT["distinct"] = lambda lst: list(dict.fromkeys(lst))
SAFE_EVAL_DICT["element"] = lambda lst, index: lst[index]
SAFE_EVAL_DICT["flatten"] = flatten
SAFE_EVAL_DICT["index"] = lambda lst, value: lst.index(value)
SAFE_EVAL_DICT["keys"] = lambda map_input: list(map_input.keys())
SAFE_EVAL_DICT["length"] = len
SAFE_EVAL_DICT["list"] = lambda *args: list(args)
SAFE_EVAL_DICT["lookup"] = lambda map_input, key, default: map_input.get(key, default)
SAFE_EVAL_DICT["map"] = lambda *args: wrap_func(create_map, list(args))
SAFE_EVAL_DICT["matchkeys"] = matchkeys
SAFE_EVAL_DICT["merge"] = merge
# SAFE_EVAL_DICT['range']
SAFE_EVAL_DICT["reverse"] = reverse
SAFE_EVAL_DICT["sort"] = sort
SAFE_EVAL_DICT["zipmap"] = lambda *lists: dict(zip(*lists))  # noqa: B905


# type conversion
SAFE_EVAL_DICT["tobool"] = lambda arg: wrap_func(tobool, arg)
SAFE_EVAL_DICT["tolist"] = lambda *args: list(*args)
# SAFE_EVAL_DICT["tomap"] = lambda arg: wrap_func(tomap, str(arg))
SAFE_EVAL_DICT["tonumber"] = lambda arg: arg if type(arg) in [int, float] else wrap_func(tonumber, arg)
SAFE_EVAL_DICT["toset"] = lambda origin: set(origin)
SAFE_EVAL_DICT["tostring"] = lambda arg: arg if isinstance(arg, str) else wrap_func(tostring, str(arg))

# encoding
SAFE_EVAL_DICT["jsonencode"] = lambda arg: arg

# date functions
SAFE_EVAL_DICT["timestamp"] = lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
SAFE_EVAL_DICT["timeadd"] = timeadd
SAFE_EVAL_DICT["formatdate"] = formatdate


def get_asteval() -> Interpreter:
    # asteval provides a safer environment for evaluating expressions by restricting the operations to a secure subset, significantly reducing the risk of executing malicious code.
    return Interpreter(
        symtable=SAFE_EVAL_DICT,
        use_numpy=False,
        minimal=True
    )


def evaluate(input_str: str) -> Any:
    """
    Safely evaluate a Terraform-like function expression using a predefined function map.
    Falls back gracefully if evaluation fails.
    """
    if not input_str or input_str == "...":
        # don't create an Ellipsis object
        return input_str
    if input_str.startswith("try"):
        # As `try` is a saved word in python, we can't override it like other functions as `eval` won't accept it.
        # Instead, we are manually replacing this string with our own custom string, so we can pass it to `eval`.

        # Don't use str.replace to make sure we replace just the first occurrence
        input_str = f"{TRY_STR_REPLACEMENT}{input_str[3:]}"
    asteval = get_asteval()
    log_level = os.getenv("LOG_LEVEL")
    should_log_asteval_errors = log_level == "DEBUG"
    if RANGE_PATTERN.match(input_str):
        temp_eval = asteval(input_str, show_errors=should_log_asteval_errors)
        evaluated = input_str if temp_eval < 0 else temp_eval
    else:
        evaluated = asteval(input_str, show_errors=should_log_asteval_errors)

    if asteval.error:
        error_messages = [err.get_error() for err in asteval.error]
        raise ValueError(f"Safe evaluation error: {error_messages}")

    return evaluated if not isinstance(evaluated, str) else remove_unicode_null(evaluated)


def remove_unicode_null(input_str: str) -> str:
    return input_str.replace("\u0000", "\\0")
