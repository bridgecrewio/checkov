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
