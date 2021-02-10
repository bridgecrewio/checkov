def force_list (var):
    if not isinstance(var, list):
        var = [var]
    return var


def force_int (var):
    try:
        if not isinstance(var, int):
            var = int(var)
        return var
    except:
        return None


def convert_str_to_bool(bool_str):
    if bool_str in ['true', '"true"', 'True', '"True"']:
        return True
    elif bool_str in ['false', '"false"', 'False', '"False"']:
        return False
    else:
        return bool_str


def force_dict(obj):
    """
    If the specified object is a dict, returns the object. If the object is a list of length 1 or more, and the first
    element is a dict, returns the first element. Else returns None.
    :param obj:
    :return:
    """
    if type(obj) == dict:
        return obj
    if type(obj) == list and len(obj) > 0 and type(obj[0]) == dict:
        return obj[0]
    return None
