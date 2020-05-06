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
