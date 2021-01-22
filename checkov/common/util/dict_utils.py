def getInnerDict(source_dict, path_as_list):
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