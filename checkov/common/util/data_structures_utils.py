from typing import Generator, Any, Union


def get_inner_dict(source_dict, path_as_list):
    result = source_dict
    for index in path_as_list:
        result = result[index]
    return result


def merge_dicts(*dicts):
    """
    Merges two or more dicts. If there are duplicate keys, later dict arguments take precedence.

    Null, empty, or non-dict arguments are qiuetly skipped.
    :param dicts:
    :return:
    """
    res = {}
    for d in dicts:
        if not d or type(d) != dict:
            continue
        res = {**res, **d}
    return res


def generator_reader_wrapper(g: Generator) -> Union[None, Any]:
    try:
        return next(g)
    except StopIteration:
        return
