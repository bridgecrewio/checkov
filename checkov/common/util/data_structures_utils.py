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

def search_deep_keys(searchText, obj, path):
    """Search deep for keys and get their values"""
    keys = []
    if isinstance(obj, dict):
        for key in obj:
            pathprop = path[:]
            pathprop.append(key)
            if key == searchText:
                pathprop.append(obj[key])
                keys.append(pathprop)
                # pop the last element off for nesting of found elements for
                # dict and list checks
                pathprop = pathprop[:-1]
            if isinstance(obj[key], dict):
                keys.extend(search_deep_keys(searchText, obj[key], pathprop))
            elif isinstance(obj[key], list):
                for index, item in enumerate(obj[key]):
                    pathproparr = pathprop[:]
                    pathproparr.append(index)
                    keys.extend(search_deep_keys(searchText, item, pathproparr))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            pathprop = path[:]
            pathprop.append(index)
            keys.extend(search_deep_keys(searchText, item, pathprop))

    return keys