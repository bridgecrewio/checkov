import itertools
import logging
import re
from functools import reduce
from math import ceil, floor, log

from checkov.terraform.parser_functions import tonumber, FUNCTION_FAILED, create_map, tobool, tomap, tostring

"""
This file contains a custom implementation of the builtin `eval` function.
`eval` is not a safe function, because it can execute *every* command, 
so this file overrides `eval` and allows only the functions in SAFE_EVAL_DICT.

The functions are an implementation of Terraform's built-in functions
https://www.terraform.io/docs/configuration/functions.html

Not all of the functions are implemented yet. If a function doesn't exist, the original value is returned.
"""


def _find_regex_groups(pattern, input_str):
    match = re.match(pattern, input_str)
    if match:
        if match.groupdict():
            # try to find named capturing groups
            return match.groupdict()
        if list(match.groups()):
            # try to find unnamed capturing groups
            return list(match.groups())
    return None


def regex(pattern, input_str):
    try:
        groups = _find_regex_groups(pattern, input_str)
        if groups is not None:
            return groups

        results = re.findall(pattern, input_str)
        # return first match
        if len(results) > 0:
            return results[0]
        return ''
    except TypeError:
        return f'regex({pattern}, {input_str})'


def regexall(pattern, input_str):
    try:
        groups = _find_regex_groups(pattern, input_str)
        if groups is not None:
            return groups

        results = re.findall(pattern, input_str)
        return results
    except TypeError:
        return f'regexall({pattern}, {input_str})'


def trim(input_str, chars_to_remove):
    for c in chars_to_remove:
        input_str = input_str.replace(c, '')
    return input_str


def coalesce(*arg):
    return reduce(lambda x, y: x if x not in [None, ""] else y, arg)


def coalesce_list(*arg):
    return reduce(lambda x, y: x if x not in [None, []] else y, arg)


def flatten(lst):
    res = [item for sublist in lst for item in sublist]
    if any(type(elem) is list for elem in res):
        return flatten(res)
    else:
        return res


def matchkeys(values_list, keys_list, search_set):
    matching = set()
    for search in search_set:
        indices = [i for i, x in enumerate(keys_list) if x == search]
        for i in indices:
            matching.add(values_list[i])

    return list(matching)


def reverse(lst):
    lst.reverse()
    return lst


def sort(lst):
    lst.sort()
    return lst


def merge(*args):
    res = {}
    for d in args:
        res = {**res, **d}
    return res


def wrap_func(f, *args):
    res = f(*args)
    if res == FUNCTION_FAILED:
        raise ValueError
    return res


SAFE_EVAL_FUNCTIONS = []
SAFE_EVAL_DICT = dict([(k, locals().get(k, None)) for k in SAFE_EVAL_FUNCTIONS])

# math functions
SAFE_EVAL_DICT['abs'] = abs
SAFE_EVAL_DICT['ceil'] = ceil
SAFE_EVAL_DICT['floor'] = floor
SAFE_EVAL_DICT['log'] = log
SAFE_EVAL_DICT['max'] = max
SAFE_EVAL_DICT['min'] = min
SAFE_EVAL_DICT['parsint'] = int
SAFE_EVAL_DICT['pow'] = pow
SAFE_EVAL_DICT['signum'] = lambda x: -1 if x < 0 else 0 if x == 0 else 1

# string functions
SAFE_EVAL_DICT['chomp'] = lambda x: x.rstrip()
SAFE_EVAL_DICT['format'] = lambda text_to_format, *args: (text_to_format % args)
SAFE_EVAL_DICT['formatlist'] = lambda text_to_format, args_list: [(text_to_format % args) for args in args_list]
SAFE_EVAL_DICT['indent'] = lambda num_of_space, input_str: input_str
SAFE_EVAL_DICT['join'] = lambda separator, lst: separator.join(lst)
SAFE_EVAL_DICT['lower'] = lambda input_str: input_str.lower()
SAFE_EVAL_DICT['regex'] = regex
SAFE_EVAL_DICT['regexall'] = regexall
SAFE_EVAL_DICT['replace'] = lambda string, substring, replacement: string.replace(substring, replacement)
SAFE_EVAL_DICT['split'] = lambda separator, input_str: input_str.split(separator)
SAFE_EVAL_DICT['strrev'] = lambda input_str: input_str[::-1]
SAFE_EVAL_DICT['substr'] = lambda input_str, offset, length: input_str[offset:offset + length]
SAFE_EVAL_DICT['title'] = lambda input_str: input_str.title()
SAFE_EVAL_DICT['trim'] = trim
SAFE_EVAL_DICT['trimprefix'] = lambda input_str, prefix: input_str.lstrip(prefix)
SAFE_EVAL_DICT['trimsuffix'] = lambda input_str, prefix: input_str.rstrip(prefix)
SAFE_EVAL_DICT['trimspace'] = lambda input_str: input_str.strip()
SAFE_EVAL_DICT['upper'] = lambda input_str: input_str.upper()

# collections
SAFE_EVAL_DICT['chunklist'] = lambda lst, chunk_size: [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
SAFE_EVAL_DICT['coalesce'] = coalesce
SAFE_EVAL_DICT['coalescelist'] = coalesce_list
SAFE_EVAL_DICT['compact'] = lambda lst: list(filter(lambda l: l != "", lst))
SAFE_EVAL_DICT['concat'] = lambda *lists: list(itertools.chain(*lists))
SAFE_EVAL_DICT['contains'] = lambda lst, value: value in lst
SAFE_EVAL_DICT['distinct'] = lambda lst: list(dict.fromkeys(lst))
SAFE_EVAL_DICT['element'] = lambda lst, index: lst[index]
SAFE_EVAL_DICT['flatten'] = flatten
SAFE_EVAL_DICT['index'] = lambda lst, value: lst.index(value)
SAFE_EVAL_DICT['keys'] = lambda map_input: list(map_input.keys())
SAFE_EVAL_DICT['length'] = len
SAFE_EVAL_DICT['list'] = lambda *args: list(args)
SAFE_EVAL_DICT['lookup'] = lambda map_input, key, default: map_input.get(key, default)
SAFE_EVAL_DICT['map'] = lambda *args: wrap_func(create_map, list(args))
SAFE_EVAL_DICT['matchkeys'] = matchkeys
SAFE_EVAL_DICT['merge'] = merge
# SAFE_EVAL_DICT['range']
SAFE_EVAL_DICT['reverse'] = reverse
SAFE_EVAL_DICT['sort'] = sort


# type conversion
SAFE_EVAL_DICT['tobool'] = lambda arg: wrap_func(tobool, arg)
SAFE_EVAL_DICT['tolist'] = lambda *args: list(*args)
SAFE_EVAL_DICT['tomap'] = lambda arg: wrap_func(tomap, str(arg))
SAFE_EVAL_DICT['tonumber'] = lambda arg: arg if type(arg) in [int, float] else wrap_func(tonumber, arg)
SAFE_EVAL_DICT['toset'] = lambda origin: set(origin)
SAFE_EVAL_DICT['tostring'] = lambda arg: arg if isinstance(arg, str) else wrap_func(tostring, str(arg))

# encoding
SAFE_EVAL_DICT['jsonencode'] = lambda arg: arg


def evaluate(input_str):
    if "__" in input_str:
        logging.warning(f"got a substring with double underscore, which is not allowed. origin string: {input_str}")
        return input_str
    return eval(input_str, {"__builtins__": None}, SAFE_EVAL_DICT)  # nosec

